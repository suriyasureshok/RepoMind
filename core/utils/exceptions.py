class RepoMindError(Exception):
    def __init__(self, message: str, *, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(RepoMindError):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class QueueError(RepoMindError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class JobStoreError(RepoMindError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class WorkspaceError(RepoMindError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class WorkerError(RepoMindError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class JobNotFoundError(NotFoundError):
    def __init__(self, job_id: str):
        super().__init__(f"Job not found: {job_id}")
