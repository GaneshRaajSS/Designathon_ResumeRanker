import json
import os
import re
from auth.login import AuthenticationManager
from services.similar_service import SimilarityService
from services.ranking_service import RankingService
from utils.exceptions import *
from utils.file_handler import FileHandler
from datetime import datetime
from utils.common_titles import common_titles

class DocumentSimilarityApp:
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.file_handler = FileHandler()
        self.current_user = None

        # Load known skills from file once
        with open('skills_list.txt', 'r') as f:
            self.known_skills = [line.strip().lower() for line in f.readlines() if line.strip()]

        # Synonyms dictionary for skill normalization
        self.synonyms = {
            "ml": "machine learning",
            "genai": "generative ai",
            "nlp": "natural language processing",
            "natural language processing(nlp)": "natural language processing",
            "llm": "large language model",
        }
        self.similarity_service = SimilarityService(
            known_skills=self.known_skills,
            synonyms=self.synonyms,
            fuzzy_threshold=0.8
        )
        self.ranking_service = RankingService()
#Skills Normalizer--------------------------------------------------------------------------
    def normalize_skills(self, skills):
        # Normalize skills by applying synonyms dictionary and lowercasing
        normalized = []
        for s in skills:
            s_lower = s.lower().strip()
            normalized.append(self.synonyms.get(s_lower, s_lower))
        return normalized
#Roles Checker--------------------------------------------------------------------------
    def requires_role(required_roles):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if not self.current_user:
                    print("❌ You must be logged in.")
                    return
                user_role = self.auth_manager.get_current_user_role()
                if user_role not in required_roles:
                    print(f"❌ Access denied. Requires role(s): {', '.join(required_roles)}")
                    return
                return func(self, *args, **kwargs)

            return wrapper

        return decorator

    def display_banner(self):
        print("="*60)
        print("   DOCUMENT SIMILARITY COMPARISON & RANKING SYSTEM")

    def display_menu(self):
        user_role = self.auth_manager.get_current_user_role()
        print("\n📋 MAIN MENU")

        options = {}

        if user_role == "admin":
            options["1"] = "Upload Job Description"
            options["2"] = "Generate Report"

        elif user_role == "recruiter":
            options["1"] = "Upload Resume"
            options["2"] = "Compare Documents"
            options["3"] = "View Profiles"
            options["4"] = "View Ranking Results"

        # Common options
        common_start = len(options) + 1
        options[str(common_start)] = "Logout"
        options[str(common_start + 1)] = "Exit"

        for key, value in options.items():
            print(f"{key}. {value}")


#LOGIN--------------------------------------------------------------------------
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
#JD INPUTS--------------------------------------------------------------------------
    @requires_role(['admin'])
    def upload_job_description(self):
        try:
            title = input("Enter Job Title: ").strip()
            description = input("Paste Job Description: ").strip()
            skills_input = input("Enter required skills (comma-separated, nospace): ").strip()
            skills = [s.strip().lower() for s in skills_input.split(',') if s.strip()]

            if not description:
                print("❌ Description cannot be empty.")
                return
            if not skills:
                print("❌ Skills cannot be empty.")
                return

            # Normalize skills for storage consistency
            skills = self.normalize_skills(skills)

            job_id = self.file_handler.save_job_from_input(title, description, skills)
            print(f"✅ Job posted successfully! Job ID: {job_id}")
        except Exception as e:
            print(f"❌ {e}")
#Input Resumes--------------------------------------------------------------------------
    @requires_role(['recruiter'])
    def upload_resume(self):
        try:
            print("\n📄 Upload Resume")
            use_pdf = input("Do you want to upload from PDF? (y/n): ").strip().lower()
            if use_pdf == 'y':
                self.upload_resume_from_pdf()
                return

            name = input("Full Name: ").strip()
            title = input("Job Title (e.g., Python Developer): ").strip()
            skills_input = input("List your skills (comma-separated): ").strip()
            skills = [s.strip() for s in skills_input.split(',') if s.strip()]
            try:
                experience = int(input("Years of Experience: ").strip())
            except ValueError:
                print("❌ Invalid input for experience. Please enter a number.")
                return

            description = input("Brief Description: ").strip()

            # Normalize skills before saving
            skills = self.normalize_skills(skills)

            profile = {
                "name": name,
                "title": title,
                "skills": skills,
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
#UPLOAD RESUME--------------------------------------------------------------------------
    @requires_role(['recruiter'])
    def upload_resume_from_pdf(self):
        import fitz  # PyMuPDF
        try:
            pdf_path = input("Enter path to the PDF file: ").strip()
            if not os.path.exists(pdf_path):
                print("❌ File not found.")
                return

            with fitz.open(pdf_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()

            lines = [line.strip() for line in text.split('\n') if line.strip()]
            import re
            def extract_name(lines):
                page_pattern = re.compile(r'page \d+ of \d+', re.I)
                page_simple_pattern = re.compile(r'page \d+', re.I)
                name_pattern = re.compile(r'^[A-Za-z\s\.\-]+$')  # simple name pattern

                for line in lines:
                    if page_pattern.match(line.lower()) or page_simple_pattern.match(line.lower()):
                        continue
                    if name_pattern.match(line):
                        # Capitalize each word nicely
                        return ' '.join(word.capitalize() for word in line.split())
                return "Unknown"

            name = extract_name(lines)
            title = next(
                (title for title in common_titles if title in text.lower()),
                "Unknown Title"
            )

            # Use loaded known skills instead of re-reading file
            known_skills = self.known_skills

            text_lower = text.lower()
            found_skills = [skill for skill in known_skills if skill in text_lower]
            skills = list(set(found_skills))

            # Normalize skills found
            skills = self.normalize_skills(skills)

            experience_match = re.search(r'(\d+)\+?\s*years?', text_lower)
            experience = int(experience_match.group(1)) if experience_match else 0

            description = '\n'.join(lines[1:])[:500]

            profile = {
                "name": name,
                "title": title,
                "skills": skills,
                "experience": experience,
                "description": description
            }

            filename = f"profile_{name.lower().replace(' ', '_')}.json"
            filepath = os.path.join(self.file_handler.profiles_dir, filename)

            with open(filepath, 'w') as f:
                json.dump(profile, f, indent=2)

            print(f"✅ Resume extracted and saved from PDF as {filename}")

        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
#VIEW PROFILES--------------------------------------------------------------------------
    def view_profiles(self):
        try:
            profiles = self.file_handler.get_all_profiles()
            print("\n👥 AVAILABLE PROFILES:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile.get('name')} - {profile.get('title')}")
        except Exception as e:
            print(f"❌ {e}")
#Compare Docs--------------------------------------------------------------------------
    @requires_role(['recruiter'])
    def compare_documents(self):
        try:
            jobs = self.file_handler.get_all_jobs()
            profiles = self.file_handler.get_all_profiles()

            if not jobs:
                print("❌ No job descriptions available.")
                return
            if not profiles:
                print("❌ No profiles available.")
                return

            print("\nAvailable Jobs:")
            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job.get('title')}")

            try:
                choice = int(input("Select job number to compare: ")) - 1
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
                return

            if choice < 0 or choice >= len(jobs):
                print("❌ Invalid choice.")
                return

            selected_job = jobs[choice]

            # Ensure experience_level is set using fallback keys
            if 'experience_level' not in selected_job:
                exp = selected_job.get('min_experience') or selected_job.get('experience') or 0
                selected_job['experience_level'] = self.similarity_service._map_experience(exp)

            similarities = []
            for profile in profiles:
                # Normalize skills inside SimilarityService; ensure your service uses self.synonyms
                score = self.similarity_service.calculate_similarity(selected_job, profile)
                # print(f"Comparing profile '{profile.get('name')}' => Score: {score}")
                similarities.append({'profile': profile, 'score': score, 'job_id': selected_job.get('id')})

            ranked = self.ranking_service.rank_profiles(similarities)
            self.file_handler.save_comparison_results(selected_job.get('id'), ranked)

            print("\n🔥 Top 3 Matches:")
            for i, match in enumerate(ranked[:3], 1):
                print(f"{i}. {match['profile'].get('name')} - Score: {match['score']}%")

        except Exception as e:
            print(f"❌ {e}")
#View Ranking Results--------------------------------------------------------------------------
    def view_ranking_results(self):
        try:
            results = self.file_handler.get_comparison_results()
            if not results:
                print("❌ No ranking results found.")
                return

            for job_id, matches in results.items():
                print(f"\nJob ID: {job_id}")
                for i, match in enumerate(matches, 1):
                    prof = match.get('profile', {})
                    name = prof.get('name', 'Unknown')
                    title = prof.get('title', 'Unknown')
                    score = match.get('score', 'N/A')
                    print(f"{i}. {name} - {title} - Score: {score}%")


        except Exception as e:
            print(f"❌ {e}")
#Generate Reports--------------------------------------------------------------------------
    @requires_role(['admin'])
    def generate_report(self):
        try:
            results = self.file_handler.get_comparison_results()
            if not results:
                print("❌ No ranking results to generate report.")
                return

            report_lines = []
            for job_id, matches in results.items():
                report_lines.append(f"Job ID: {job_id}")
                for i, match in enumerate(matches, 1):
                    # prof = match['profile']
                    prof = match.get('profile', {})

                    # line = f"{i}. {prof.get('name')} - {prof.get('title')} - Score: {match['score']}%"
                    name = prof.get('name', 'Unknown')
                    title = prof.get('title', 'Unknown')
                    score = match.get('score', 'N/A')
                    line = f"{i}. {name} - {title} - Score: {score}%"

                    report_lines.append(line)
                report_lines.append("\n")
            report_dir = "reports"
            os.makedirs(report_dir, exist_ok=True)
            report_path = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(report_path, 'w') as f:
                f.write('\n'.join(report_lines))

            print(f"✅ Report generated at {report_path}")

        except Exception as e:
            print(f"❌ {e}")
#Logout --------------------------------------------------------------------------
    def logout(self):
        self.current_user = None
        print("✅ Logged out successfully.")
#MAIN FILE--------------------------------------------------------------------------
    def run(self):
        self.display_banner()

        if not self.login_flow():
            print("Exiting application.")
            return

        while True:
            user_role = self.auth_manager.get_current_user_role()
            options = {}

            # Role-specific options
            if user_role == "admin":
                options["1"] = ("Upload Job Description", self.upload_job_description)
                options["2"] = ("Generate Report", self.generate_report)

            elif user_role == "recruiter":
                options["1"] = ("Upload Resume", self.upload_resume)
                options["2"] = ("Compare Documents", self.compare_documents)
                options["3"] = ("View Profiles", self.view_profiles)
                options["4"] = ("View Ranking Results", self.view_ranking_results)

            # Common options (added after role-specific ones)
            next_index = str(len(options) + 1)
            options[next_index] = ("Logout", self.logout)
            exit_index = str(int(next_index) + 1)
            options[exit_index] = ("Exit", None)

            # Display menu
            print("\n📋 MAIN MENU")
            for key, (label, _) in options.items():
                print(f"{key}. {label}")

            # Get choice
            choice = input("Enter your choice: ").strip()

            # Execute selected option
            if choice in options:
                label, action = options[choice]

                if label == "Logout":
                    action()
                    if not self.login_flow():
                        print("Exiting application.")
                        break
                elif label == "Exit":
                    print("👋 Goodbye!")
                    break
                else:
                    action()
            else:
                print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    app = DocumentSimilarityApp()
    app.run()

