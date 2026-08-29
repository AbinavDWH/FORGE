class ForgeError(Exception):
    """Base FORGE error."""


class InvalidStateError(ForgeError):
    """Raised when an entity is missing or in an invalid pipeline state."""


class TaskNotFoundError(ForgeError):
    """Raised when a schedule task cannot be found."""


class DependencyViolationError(ForgeError):
    """Raised when an update would break CPM dependency logic."""