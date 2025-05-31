import math
import re
from difflib import get_close_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimilarityService:
    def __init__(self, known_skills, synonyms=None, fuzzy_threshold=0.8):
        """
        known_skills: list of known skill strings (all lowercase)
        synonyms: dict of skill synonyms mapping variant -> normalized skill
        fuzzy_threshold: float (0-1) threshold for fuzzy skill matching
        """
        self.known_skills = known_skills
        self.synonyms = synonyms or {}
        self.fuzzy_threshold = fuzzy_threshold
        self.vectorizer = TfidfVectorizer()

    def _tokenize(self, text):
        return re.findall(r'\w+', text.lower())

    def _normalize_skill(self, skill):
        skill = skill.lower().strip()
        # map synonyms first
        if skill in self.synonyms:
            return self.synonyms[skill]

        # fuzzy match to known skills
        matches = get_close_matches(skill, self.known_skills, n=1, cutoff=self.fuzzy_threshold)
        if matches:
            return matches[0]

        return skill

    def _normalize_skill_set(self, skills):
        return set(self._normalize_skill(s) for s in skills)

    def calculate_similarity(self, job, profile):
        # Normalize skills
        job_skills = self._normalize_skill_set(job.get("required_skills", []))
        profile_skills = self._normalize_skill_set(profile.get("skills", []))

        # Skill overlap using Jaccard similarity
        if not job_skills:
            skill_overlap = 0
        else:
            skill_overlap = len(job_skills & profile_skills) / len(job_skills | profile_skills or [1])

        # Experience match mapping
        exp_match = 1.0 if job.get("experience_level") == self._map_experience(profile.get("experience", 0)) else 0.5

        # Text similarity with TF-IDF + cosine similarity
        text_sim = self._tfidf_cosine_sim(job.get("description", ""), profile.get("description", ""))

        # Weighted score: skills 60%, experience 30%, text 10%
        score = (skill_overlap * 0.6 + exp_match * 0.3 + text_sim * 0.1) * 100
        return round(score, 2)

    def _map_experience(self, years):
        if years >= 7:
            return "senior"
        elif years >= 4:
            return "mid"
        return "junior"

    def _tfidf_cosine_sim(self, text1, text2):
        # Fit TF-IDF on both texts and compute cosine similarity
        tfidf = self.vectorizer.fit_transform([text1, text2])
        sim_matrix = cosine_similarity(tfidf[0:1], tfidf[1:2])
        return sim_matrix[0][0] if sim_matrix.size else 0
