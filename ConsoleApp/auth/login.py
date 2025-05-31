
class AuthenticationManager:
    def __init__(self):
        self.users = {
            "admin": {"password" : "admin123", "role" : "admin"},
            "recruiter": {"password" : "recruiter123", "role" : "recruiter"},
            "employee": {"password" : "employee123", "role" : "employee"}
        }
    def authenticate(self, username, password):
        user = self.users.get(username)
        if not user or user["password"] != password:
            return False
        self.current_user_role = user["role"]
        return True

    def get_current_user_role(self):
        return getattr(self, "current_user_role", None)

        # return self.users.get(username) == password

