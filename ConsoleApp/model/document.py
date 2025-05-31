from dataclasses import dataclass
from typing import List
from datetime import datetime
import uuid

@dataclass
class JobDescription:
    id: str
    title: str
    description: str
    required_skills: List[str]
    experience_level: str
    created_at: datetime

    @classmethod
    def from_text(cls, title, content, skills: List[str]):
        experience = cls._extract_experience_level(content)
        return cls(str(uuid.uuid4()), title, content, skills, experience, datetime.now())

    @staticmethod
    def _extract_experience_level(content):
        text = content.lower()
        if "senior" in text:
            return "senior"
        elif "mid" in text:
            return "mid"
        return "junior"

