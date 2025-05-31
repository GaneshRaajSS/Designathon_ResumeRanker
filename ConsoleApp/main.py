# main.py
import json
from auth.login import AuthenticationManager
from services.similar_service import SimilarityService
from services.ranking_service import RankingService
from utils.exceptions import *
from utils.file_handler import FileHandler
from datetime import datetime
import os

class DocumentSimilarityApp:
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.similarity_service = SimilarityService()
        self.ranking_service = RankingService()
        self.file_handler = FileHandler()
        self.current_user = None

    def display_banner(self):
        print("="*60)
        print("   DOCUMENT SIMILARITY COMPARISON & RANKING SYSTEM")
    def display_menu(self):
        print("\n📋 MAIN MENU")
        print("1. Upload Job Description")
        print("2. Upload Resume")
        print("3. View Available Profiles")
        print("4. Compare Job with Profiles")
        print("5. View Ranking Results")
        print("6. Generate Report")
        print("7. Logout")
        print("8. Exit")

    def login_flow(self):
        try:
            print("\n🔐 LOGIN REQUIRED")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            if self.auth_manager.authenticate(username, password):
                self.current_user = username
                print(f"\n✅ Welcome, {username}!")
                return True
            else:
                print("❌ Invalid credentials.")
                return False
        except AuthenticationError as e:
            print(f"❌ {e}")
            return False

    def upload_job_description(self):
        try:
            title = input("Enter Job Title: ").strip()
            description = input("Paste Job Description: ").strip()

            if not description:
                 print("❌ Description cannot be empty.")
                 return
            job_id = self.file_handler.save_job_from_input(title, description)
            print(f"✅ Job posted successfully! Job ID: {job_id}")

        except Exception as e:
            print(f"❌ {e}")
    def upload_resume(self):
        try:
            print("\n📄 Upload Your Resume")
            name = input("Full Name: ").strip()
            title = input("Job Title (e.g., Python Developer): ").strip()
            skills = input("List your skills (comma-separated): ").strip().lower().split(',')
            experience = int(input("Years of Experience: ").strip())
            description = input("Brief Description: ").strip()

            profile = {
                "name": name,
                "title": title,
                "skills": [s.strip() for s in skills],
                "experience": experience,
                "description": description
            }

            filename = f"profile_{name.lower().replace(' ', '_')}.json"
            filepath = os.path.join(self.file_handler.profiles_dir, filename)

            with open(filepath, 'w') as f:
                json.dump(profile, f, indent=2)

            print(f"✅ Resume uploaded successfully as {filename}")

        except Exception as e:
            print(f"❌ Error uploading resume: {e}")

    def view_profiles(self):
        try:
            profiles = self.file_handler.get_all_profiles()
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile['name']} - {profile['title']} - {profile['experience']} yrs")
        except Exception as e:
            print(f"❌ {e}")

    def compare_documents(self):
        try:
            jobs = self.file_handler.get_all_jobs()
            profiles = self.file_handler.get_all_profiles()

            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job['title']}")
            choice = int(input("Select job number: ")) - 1
            selected_job = jobs[choice]

            similarities = []
            for profile in profiles:
                score = self.similarity_service.calculate_similarity(selected_job, profile)
                similarities.append({'profile': profile, 'score': score, 'job_id': selected_job['id']})

            ranked = self.ranking_service.rank_profiles(similarities)
            self.file_handler.save_comparison_results(selected_job['id'], ranked)

            print("Top 3 Matches:")
            for i, match in enumerate(ranked[:3], 1):
                print(f"{i}. {match['profile']['name']} ({match['score']:.2f}%)")

        except Exception as e:
            print(f"❌ {e}")

    def view_ranking_results(self):
        try:
            results = self.file_handler.get_comparison_results()
            for job_id, rankings in results.items():
                job = self.file_handler.get_job_by_id(job_id)
                print(f"\nJob: {job['title']}")
                for i, match in enumerate(rankings[:3], 1):
                    print(f"{i}. {match['profile']['name']} - {match['score']:.1f}%")
        except Exception as e:
            print(f"❌ {e}")

    def generate_report(self):
        try:
            results = self.file_handler.get_comparison_results()
            os.makedirs("reports", exist_ok=True)
            path = f"reports/report_{self.current_user}.txt"
            with open(path, 'w') as f:
                for job_id, matches in results.items():
                    job = self.file_handler.get_job_by_id(job_id)
                    f.write(f"Job: {job['title']}\n")
                    for match in matches[:3]:
                        f.write(f"- {match['profile']['name']} ({match['score']:.2f}%)\n")
                    f.write("\n")
            print(f"✅ Report saved to {path}")
        except Exception as e:
            print(f"❌ {e}")

    def run(self):
        self.display_banner()
        if not self.login_flow():
            return
        while True:
            self.display_menu()
            choice = input("Enter choice: ").strip()
            if choice == "1":
                self.upload_job_description()
            elif choice == "2":
                self.upload_resume()
            elif choice == "3":
                self.view_profiles()
            elif choice == "4":
                self.compare_documents()
            elif choice == "5":
                self.view_ranking_results()
            elif choice == "6":
                self.generate_report()
            elif choice == "7":
                print("Logged out.")
                if not self.login_flow():
                    break
            elif choice == "8":
                print("Goodbye!")
                break
            else:
                print("❌ Invalid choice.")

if __name__ == "__main__":
    DocumentSimilarityApp().run()
