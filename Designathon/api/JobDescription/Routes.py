from fastapi import APIRouter, UploadFile, File, HTTPException
from db.Schema import JobDescriptionResponse
from .Service import create_job_description, get_job_description
from docx import Document
import fitz, re

router = APIRouter()

@router.get("/job-descriptions/{jd_id}", response_model=JobDescriptionResponse)
def read_jd(jd_id: str):
    try:
        jd = get_job_description(jd_id)
        if not jd:
            raise HTTPException(status_code=404, detail="Job Description not found")
        return jd
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def extract_text_from_pdf(file: UploadFile) -> str:
    doc = fitz.open(stream=file.file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])


def extract_text_from_docx(file: UploadFile) -> str:
    document = Document(file.file)
    return "\n".join([para.text for para in document.paragraphs])

def clean(text):
    return text.lstrip(":").strip()
def parse_jd_fields(text: str) -> dict:
    def extract_section(start_label, next_label=None):
        pattern = rf"{start_label}[:\-]?\s*(.*?)(?=\n\s*{next_label}[:\-]|\Z)" if next_label else rf"{start_label}[:\-]?\s*(.*)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    title = extract_section("Title", "Description")
    description = extract_section("Description", "Skills")
    skills = extract_section("Skills", "Experience")
    experience = extract_section("Experience")

    return {
    "title": clean(title),
    "description": description.strip(),
    "skills": clean(skills),
    "experience": clean(experience)
}


@router.post("/job-descriptions/upload", response_model=JobDescriptionResponse)
async def upload_jd_file(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".pdf"):
            content = extract_text_from_pdf(file)
        elif file.filename.endswith(".docx"):
            content = extract_text_from_docx(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # parse fields from document
        parsed_fields = parse_jd_fields(content)

        # Validate required fields
        if not parsed_fields["title"] or not parsed_fields["skills"] or not parsed_fields["experience"]:
            raise HTTPException(status_code=400, detail="Missing required JD fields in document.")

        return await create_job_description(parsed_fields)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
