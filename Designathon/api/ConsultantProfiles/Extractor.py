import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Download required resources once
nltk.download('punkt')

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

#
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
                    break
                if re.search(r'working with|currently at|experience|from .* to|till date', clean):
                    break
                if line.strip() and line.strip() not in seen_lines:
                    section_lines.append(line.strip())
                    seen_lines.add(line.strip())

    full_text = "\n".join(section_lines).strip()
    return full_text if section_lines else None
#

def extract_yoe(text: str) -> str | None:
    # regex to match patterns like "2 years", "3+ years", "2.5 years", etc.
    match = re.search(r'(\d+(\.\d+)?\s*\+?\s*years?)', text, re.IGNORECASE)
    return match.group(1).strip() if match else None

#
def extract_sections(text: str) -> dict:
    experience_text = extract_by_section(
        text,
        ["Synopsis"],
        ["Experience Summary", "Education", "Project Experience", "Areas of Experience", "Qualification"]
    )

    yoe = extract_yoe(experience_text or "")

    # Sentence tokenization
    sentences = sent_tokenize(text)
    
    # Word tokenization (you can also store or use these as needed)
    tokenized_sentences = [word_tokenize(sent) for sent in sentences]

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_by_section(
            text,
            ["Skills", "Technical Skills", "Areas of Experience"],
            ["Experience", "Education", "Qualification", "Page"]
        ),
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

#