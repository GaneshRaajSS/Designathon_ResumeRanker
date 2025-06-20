from fpdf import FPDF
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from io import BytesIO
import os
import matplotlib.pyplot as plt
import tempfile
from difflib import SequenceMatcher
from skills import known_skills

class ReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, "Consultant Resume Ranking Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 0, "C")

# ... [skill matching helpers stay unchanged]
def normalize_and_filter_skills(raw_skills: str) -> list[str]:
    cleaned = []
    for s in raw_skills.split(','):
        s_clean = s.strip().lower()
        if s_clean:
            mapped = map_to_known_skill(s_clean)
            if mapped:
                cleaned.append(mapped)
    return cleaned

def map_to_known_skill(skill: str) -> str | None:
    """Fuzzy map a skill to the closest known skill."""
    best_match = None
    best_score = 0.0
    for known in known_skills:
        score = SequenceMatcher(None, skill, known).ratio()
        if score > best_score:
            best_score = score
            best_match = known
    return best_match if best_score >= 0.75 else None

def fuzzy_skill_match(skill: str, skill_list: list[str]) -> bool:
    for s in skill_list:
        if SequenceMatcher(None, skill, s).ratio() >= 0.8:
            return True
    return False

def extract_missing_skills_from_gpt(jd_skills: list[str], consultant_skills: list[str], gpt_comment: str) -> list[str]:
    explanation = gpt_comment.lower()

    if any(keyword in explanation for keyword in [
        "possesses all the required skills",
        "has all the required skills",
        "no missing skills",
        "skills match (30/30)"
    ]):
        return []

    # fallback to fuzzy matching
    return [skill for skill in jd_skills if not fuzzy_skill_match(skill, consultant_skills)]


def clean_gpt_explanation(explanation: str) -> str:
    lines = explanation.strip().splitlines()
    cleaned = [
        line for line in lines
        if not line.strip().lower().startswith("score:") and not line.strip().lower().startswith("overall")
    ]
    return "\n".join(cleaned).strip()

def generate_sas_url(blob_path: str) -> str:
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_path}"

def generate_consultant_report(jd_id: str, consultants: list[dict], jd_obj=None) -> str:
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    # Job Description Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Job Description", ln=True, fill=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Title: {jd_obj.title}", ln=True)
    pdf.cell(0, 8, f"Skills: {jd_obj.skills}", ln=True)
    pdf.cell(0, 8, f"Experience: {jd_obj.experience}", ln=True)
    pdf.cell(0, 8, f"End Date: {jd_obj.end_date.strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)

    # Section: Consultant Table
    pdf.set_fill_color(230, 230, 255)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Top Ranked Consultants", ln=True, fill=True)
    pdf.ln(3)

    jd_skills_list = normalize_and_filter_skills(jd_obj.skills if jd_obj else "")
    labels, scores = [], []

    for i, c in enumerate(consultants, 1):
        name = c.get("name", "Unknown")
        email = c.get("email", "Unknown")
        score = c.get("score", 0)
        explanation = c.get("explanation", "No GPT explanation provided.")
        consultant_skills_list = normalize_and_filter_skills(c.get("skills", ""))
        missing_skills = extract_missing_skills_from_gpt(jd_skills_list, consultant_skills_list, explanation)
        cleaned_explanation = clean_gpt_explanation(explanation)
        

        labels.append(name)
        scores.append(score)

        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(0)
        pdf.cell(0, 8, f"{i}. {name}", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"Email: {email}", ln=True)
        pdf.cell(0, 6, f"Score: {score:.2f}", ln=True)

        if missing_skills:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 6, f"Missing Skills: {', '.join(missing_skills)}", ln=True)
            pdf.set_text_color(0, 0, 0)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, cleaned_explanation)
        pdf.ln(1)

    # ---- Charts (side by side) ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Pie Chart
    ax1.pie(scores, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.set_title("Score Distribution")

    # Bar Chart
    ax2.bar(labels, scores, color='skyblue')
    ax2.set_ylabel('Score')
    ax2.set_title('Consultant Scores')
    ax2.tick_params(axis='x', rotation=45)

    # Save single combined chart
    chart_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(0, 10, "Visual Summary", ln=True, fill=True)
    pdf.image(chart_path, x=15, y=None, w=180)
    pdf.ln(10)

    # --- Save and Upload
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(pdf_bytes)
    blob_name = f"reports/{jd_id}/consultant_report.pdf"
    blob_service = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(buffer, overwrite=True)

    return generate_sas_url(blob_name)
