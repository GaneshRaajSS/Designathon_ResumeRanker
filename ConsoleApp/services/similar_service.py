import math
import re

class SimilarityService:
    def _tokenize(self, text):
        return re.findall(r'\w+', text.lower())

    def calculate_similarity(self, job, profile):
        job_skills = set(skill.lower() for skill in job["required_skills"])
        profile_skills = set(skill.lower() for skill in profile["skills"])
        skill_overlap = len(job_skills & profile_skills) / len(job_skills | profile_skills or [1])

        exp_match = 1.0 if job["experience_level"] == self._map_experience(profile["experience"]) else 0.5

        text_sim = self._cosine_sim(job["description"], profile["description"])

        return round((skill_overlap * 0.4 + exp_match * 0.3 + text_sim * 0.3) * 100, 2)

    def _map_experience(self, years):
        if years >= 7:
            return "senior"
        elif years >= 4:
            return "mid"
        return "junior"

    def _cosine_sim(self, t1, t2):
        words1 = self._tokenize(t1)
        words2 = self._tokenize(t2)
        all_words = list(set(words1 + words2))
        v1 = [words1.count(w) for w in all_words]
        v2 = [words2.count(w) for w in all_words]
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        return dot / (mag1 * mag2) if mag1 and mag2 else 0
