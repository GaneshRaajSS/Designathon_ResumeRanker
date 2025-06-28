import re
import os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from openai import AzureOpenAI
from skills import skill_lookup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

nltk.data.path.append(os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'nltk_data'))
nltk.download('punkt')

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")

def extract_name(text: str) -> str | None:
    lines = text.strip().splitlines()
    for line in lines[:10]:
        line = line.strip()
        if re.match(r'^[A-Z][A-Z\s]{3,}$', line):
            return line.title()
        if re.match(r'^[A-Z][a-z]+\s[A-Z][a-z]+.*$', line):
            return line.strip()
    return None

def extract_email(text: str) -> str | None:
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str | None:
    match = re.search(r'\+?\d[\d\s\-\(\)]{8,}\d', text)
    return match.group(0) if match else None

def extract_by_section(text: str, headers, stop_words=None):
    lines = text.splitlines()
    section_lines = []
    capturing = False
    seen_lines = set()

    for line in lines:
        clean = line.strip().lower()

        for h in headers:
            if h.lower() in clean:
                capturing = True
                parts = re.split(rf'{re.escape(h)}[:\-]?', line, flags=re.IGNORECASE)
                if len(parts) > 1 and parts[1].strip():
                    content = parts[1].strip()
                    if content not in seen_lines:
                        section_lines.append(content)
                        seen_lines.add(content)
                break
        else:
            if capturing:
                if stop_words and any(s.lower() in clean for s in stop_words):
                    capturing = False
                    continue
                if re.search(r'working with|currently at|experience|from .* to|till date', clean):
                    continue
                if line.strip() and line.strip() not in seen_lines:
                    section_lines.append(line.strip())
                    seen_lines.add(line.strip())

    full_text = "\n".join(section_lines).strip()
    return full_text if section_lines else None

async def gpt_extract_yoe(text: str) -> str | None:
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts and calculates **only** total full-time professional work experience from resumes.\n"
                "🟡 Ignore internships, trainings, part-time, and academic projects.\n"
                "🔵 If a date is marked 'Till date', treat it as June 2025.\n"
                "🟢 Convert months into years with 1 decimal point precision.\n\n"
                "✔ Examples:\n"
                "• Jan 2020 – Jan 2022 → 2.0\n"
                "• Oct 2024 – Till date (assume today is June 2025) → 0.8\n"
                "• Feb 2019 – May 2023 → 4.3\n\n"
                "Return **only a number**, like 3.5 years or 0.8 years — nothing else."
            )
        },
        {
            "role": "user",
            "content": (
                f"Resume:\n{text}\n\n"
                "What is the total professional full-time work experience?"
            )
        }
    ]

    res = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0.0,
        max_tokens=20
    )

    result = res.choices[0].message.content.strip()

    if re.match(r'^(\d+(\.\d+)?)\s*years?$', result):
        return result
    return None

def normalize_skills(raw_text: str) -> list[str]:
    words = re.split(r'[\n,;/\-]+', raw_text.lower())
    normalized = set()

    for word in words:
        cleaned = word.strip()
        if not cleaned:
            continue
        if cleaned in skill_lookup:
            normalized.add(skill_lookup[cleaned])
        else:
            simplified = re.sub(r'[\s\-]+', '', cleaned)
            for alias in skill_lookup:
                alias_simplified = re.sub(r'[\s\-]+', '', alias)
                if simplified == alias_simplified:
                    normalized.add(skill_lookup[alias])
                    break
    return sorted(normalized)

def extract_yoe(text: str) -> str | None:
    text = text.lower()
    if "intern" in text or "internship" in text:
        return None

    year_match = re.search(r'(\d+(\.\d+)?)(\+)?\s*(years?|yrs?)', text)
    if year_match:
        years = round(float(year_match.group(1)), 1)
        return f"{years} years"

    month_match = re.search(r'(\d+)\s*(months?|mos?)', text)
    if month_match:
        months = int(month_match.group(1))
        years = round(months / 12, 1)
        return f"{years} years"

    return None

async def extract_sections(text: str) -> dict:
    experience_text = extract_by_section(
        text,
        ["Synopsis"],
        ["Experience Summary", "Education", "Project Experience", "Areas of Experience", "Qualification"]
    )

    raw_skills = extract_by_section(
        text,
        [
            "Skills", "Technical Skills", "Technologies", "Tools & Technology", "Languages",
            "Areas of Experience", "AreasofExperience", "Area of EXPERIENCE", "Certifications",
            "Tools", "Platforms", "Frameworks"
        ],
        ["Experience", "Education", "Qualification", "Page", extract_name(text)]
    )
    normalized_skills = normalize_skills(raw_skills or "")

    yoe = extract_yoe(experience_text or "")
    if not yoe:
        yoe = await gpt_extract_yoe(text)

    sentences = sent_tokenize(text)
    tokenized_sentences = [word_tokenize(sent) for sent in sentences]

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": ", ".join(normalized_skills) if normalized_skills else None,
        "experience": yoe if yoe else "null",
        "education": extract_by_section(
            text,
            ["Education", "Qualification"],
            ["Projects", "Certifications"]
        ),
        "projects": extract_by_section(
            text,
            ["Projects", "Project Work", "Project Experience", "POC", "Proof of Concept"],
            ["Experience", "Education", "Qualification", "Synopsis", "Areas of Experience"]
        ),
        "sentences": sentences,
        "tokens": tokenized_sentences
    }
