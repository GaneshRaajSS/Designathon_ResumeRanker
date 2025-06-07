
class AuthenticationManager:
    def __init__(self):
        self.users = {
            "ARRequestor": {"password" : "ARRequestor123", "role" : "admin"},
            "Recruiter": {"password" : "Recruiter123", "role" : "recruiter"}
        }
    def authenticate(self, username, password):
        user = self.users.get(username)
        if not user or user["password"] != password:
            return None
        self.current_user_role = user["role"]
        return True

    def get_current_user_role(self):
        return getattr(self, "current_user_role", None)


