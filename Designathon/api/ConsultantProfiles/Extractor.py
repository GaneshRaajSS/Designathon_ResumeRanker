import re
import spacy
from skills import known_skills  # your external skills list

nlp = spacy.load("en_core_web_sm")

def extract_name(text: str) -> str | None:
    lines = text.strip().splitlines()
    for line in lines[:10]:
        line = line.strip()
        if re.match(r'^[A-Z][A-Z\s]{3,}$', line):
            return line.title()
        if re.match(r'^[A-Z][a-z]+\s[A-Z][a-z]+.*$', line):
            return line.strip()
    return None

def extract_by_header(header_keywords, text, stop_keywords=None):
    lines = text.splitlines()
    capturing = False
    section_lines = []
    for line in lines:
        clean_line = line.strip().lower()
        if any(h.lower() in clean_line for h in header_keywords):
            capturing = True
            continue
        if capturing and stop_keywords and any(s.lower() in clean_line for s in stop_keywords):
            break
        if capturing:
            section_lines.append(line)
    return "\n".join(section_lines).strip() if section_lines else None

def extract_experience_years(exp_text: str) -> str:
    if not exp_text:
        return "N/A"
    patterns = [
        r'(\d+)\s*\+?\s*(years|yrs)',
        r'(\d+)\s*(?:to|-)\s*(\d+)\s*(years|yrs)',
        r'(\d+\.\d+)\s*(years|yrs)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, exp_text, re.IGNORECASE)
        if matches:
            max_years = 0.0
            for match in matches:
                nums = [float(m) for m in match if m.replace('.', '', 1).isdigit()]
                if nums:
                    max_years = max(max_years, max(nums))
            if max_years < 3:
                return "N/A"
            if max_years.is_integer():
                return f"{int(max_years)} years"
            else:
                return f"{max_years} years"
    return "N/A"
def extract_sections(text: str) -> dict:
    doc = nlp(text)

    sections = {
        "name": None,
        "email": None,
        "phone": None,
        "skills": None,
        "experience": None,
        "experience_years": None,
        "education": None,
        "projects": None
    }

    # Extract email and phone
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone_match = re.search(r'\+?\d[\d\s\-\(\)]{8,}\d', text)
    sections["email"] = email_match.group(0) if email_match else None
    sections["phone"] = phone_match.group(0) if phone_match else None

    # Extract name
    extracted_name = extract_name(text)
    if extracted_name:
        sections["name"] = extracted_name
    else:
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                sections["name"] = ent.text.strip()
                break

    # Extract skills
    found_skills = set()
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        for skill in known_skills:
            if skill in chunk_text:
                found_skills.add(skill)
    for token in doc:
        token_lower = token.text.lower()
        if token_lower in known_skills:
            found_skills.add(token_lower)
    formatted_skills = sorted(skill.title() for skill in found_skills)
    sections["skills"] = ", ".join(formatted_skills) if formatted_skills else None

    # Extract experience section text by header, else use whole text
    exp_text = extract_by_header(["Experience", "Work Experience", "Professional Experience"], text, ["Education", "Projects"])
    if exp_text:
        sections["experience"] = exp_text.strip()
        sections["experience_years"] = extract_experience_years(exp_text)
    else:
        sections["experience"] = None
    sections["experience_years"] = "N/A"


    # Extract clean years from experience text
    sections["experience_years"] = extract_experience_years(exp_text)

    # Extract education and projects
    sections["education"] = extract_by_header(["Education", "Qualifications"], text, ["Projects", "Experience"])
    sections["projects"] = extract_by_header(["Projects", "Project Work"], text, ["Experience", "Education"])

    return sections
