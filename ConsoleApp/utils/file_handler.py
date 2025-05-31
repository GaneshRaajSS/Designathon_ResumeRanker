import os
import json
from model.document import JobDescription

class FileHandler:
    def __init__(self):
        self.jobs_dir = "data/job_descriptions"
        self.profiles_dir = "data/profiles"
        self.results_file = "data/comparison_results.json"
        os.makedirs(self.jobs_dir, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)

    def read_document(self, path):
        with open(path, 'r') as f:
            return f.read()

    def save_job_from_input(self, title, content, skills):
        job = JobDescription.from_text(title, content, skills)
        file_path = os.path.join(self.jobs_dir, f"{job.id}.json")
        with open(file_path, 'w') as f:
            json.dump(job.__dict__, f, indent=2, default=str)
        return job.id

    def get_all_jobs(self):
        jobs = []
        for file in os.listdir(self.jobs_dir):
            with open(os.path.join(self.jobs_dir, file)) as f:
                jobs.append(json.load(f))
        return jobs

    def get_job_by_id(self, job_id):
        path = os.path.join(self.jobs_dir, f"{job_id}.json")
        with open(path) as f:
            return json.load(f)

    def get_all_profiles(self):
        profiles = []
        for file in os.listdir(self.profiles_dir):
            with open(os.path.join(self.profiles_dir, file)) as f:
                profiles.append(json.load(f))
        return profiles

    def save_comparison_results(self, job_id, results):
        if os.path.exists(self.results_file):
            with open(self.results_file) as f:
                all_results = json.load(f)
        else:
            all_results = {}
        all_results[job_id] = results
        with open(self.results_file, 'w') as f:
            json.dump(all_results, f, indent=2)

    def get_comparison_results(self):
        if os.path.exists(self.results_file):
            with open(self.results_file) as f:
                return json.load(f)
        return {}
