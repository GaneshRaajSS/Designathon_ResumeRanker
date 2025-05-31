
class AuthenticationManager:
    def __init__(self):
        self.users = {
            "admin": "admin123",
            "recruiter": "recruit123",
            "employee": "employee123"
        }
    def authenticate(self, username, password):
        return self.users.get(username) == password
