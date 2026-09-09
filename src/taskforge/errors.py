class TaskForgeError(Exception):
    code = "taskforge_error"
    message = "TaskForge error"


class ProjectNotFoundError(TaskForgeError):
    code = "not_found"
    message = "Project not found"


class TaskNotFoundError(TaskForgeError):
    code = "not_found"
    message = "Task not found"


class InvalidStateTransitionError(TaskForgeError):
    code = "invalid_state_transition"
    message = "Task status cannot change directly from todo to done"
