from dataclasses import dataclass
from datetime import datetime
from typing import List
import uuid

@dataclass
class ConsultantProfile:
    id: str
    name: str
    title: str
    skills: List[str]
    experience: int
    description: str
    created_at: datetime

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("id", str(uuid.uuid4())),
            data["name"],
            data["title"],
            data["skills"],
            data["experience"],
            data.get("description", ""),
            datetime.now()
        )
