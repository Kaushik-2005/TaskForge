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


class AuthError(TaskForgeError):
    code = "auth_error"
    message = "Authentication failed"


class EmailAlreadyRegisteredError(AuthError):
    code = "email_already_registered"
    message = "Email is already registered"


class InvalidCredentialsError(AuthError):
    code = "invalid_credentials"
    message = "Invalid email or password"


class UnauthenticatedError(AuthError):
    code = "unauthenticated"
    message = "Authentication required"


class CsrfError(AuthError):
    code = "csrf_required"
    message = "Valid CSRF token required"
