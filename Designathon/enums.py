from enum import Enum


class JobStatus(str, Enum):
    in_progress = "In Progress"
    completed = "Completed"
    archived = "Archived"

class NotificationStatus(str, Enum):
    pending = "Pending"
    sent = "Sent"
    failed = "Failed"

class WorkflowStepStatus(str, Enum):
    pending = "Pending"
    completed = "Completed"
    failed = "Failed"

class UserRoleStatus(str, Enum):
    User = "User"
    ARRequestor = "ARRequestor"
    Recruiter = "Recruiter"

class HistoryStatus(str, Enum):
    Shortlisted = "Shortlisted"
    Selected = "Selected"
    Rejected = "Rejected"

    