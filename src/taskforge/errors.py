class TaskForgeError(Exception):
    code = "taskforge_error"
    message = "TaskForge error"


class ProjectNotFoundError(TaskForgeError):
    code = "not_found"
    message = "Project not found"


class WorkspaceNotFoundError(TaskForgeError):
    code = "not_found"
    message = "Workspace not found"


class ExportNotFoundError(TaskForgeError):
    code = "export_not_found"
    message = "Export not found"


class TaskNotFoundError(TaskForgeError):
    code = "not_found"
    message = "Task not found"


class InvalidStateTransitionError(TaskForgeError):
    code = "invalid_state_transition"
    message = "Task status cannot change directly from todo to done"


class PermissionDeniedError(TaskForgeError):
    code = "forbidden"
    message = "Permission denied"


class StaleTaskVersionError(TaskForgeError):
    code = "stale_task_version"
    message = "Task was modified by another request"


class UserNotFoundError(TaskForgeError):
    code = "not_found"
    message = "User not found"


class DuplicateMembershipError(TaskForgeError):
    code = "duplicate_membership"
    message = "User is already a member of this workspace"


class LastOwnerError(TaskForgeError):
    code = "last_owner"
    message = "Workspace must keep at least one owner"


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


class IdempotencyConflictError(TaskForgeError):
    code = "idempotency_conflict"
    message = "Idempotency key was already used with a different request"
