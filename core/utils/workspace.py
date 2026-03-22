# core/utils/workspace.py

import os
import re
import time
import stat
import shutil
import subprocess
from pathlib import Path

from core.config import settings
from core.logging import logger
from .exceptions import WorkspaceError


JOB_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def handle_remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


class WorkspaceManager:

    def __init__(self):
        self.base_path = Path(settings.WORKSPACE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _validate_job_id(self, job_id: str) -> None:
        if not job_id or not JOB_ID_PATTERN.match(job_id):
            raise WorkspaceError(f"Invalid job_id: {job_id}")

    def get_repo_path(self, job_id: str) -> Path:
        self._validate_job_id(job_id)

        base_resolved = self.base_path.resolve()
        repo_path = (self.base_path / f"repo_{job_id}").resolve()

        try:
            repo_path.relative_to(base_resolved)
        except ValueError as exc:
            raise WorkspaceError(f"Invalid job_id path: {job_id}") from exc

        return repo_path

    def create_workspace(self, job_id: str) -> Path:
        repo_path = self.get_repo_path(job_id)
        repo_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Workspace created: {repo_path}")
        return repo_path

    def delete_workspace(self, job_id: str):
        repo_path = self.get_repo_path(job_id)

        if not repo_path.exists():
            return

        for attempt in range(3):
            try:
                shutil.rmtree(repo_path, onerror=handle_remove_readonly)
                logger.info(f"Workspace deleted: {repo_path}")
                return
            except PermissionError:
                logger.warning(f"Retry {attempt + 1}: Failed to delete {repo_path}, retrying...")
                time.sleep(1)

        raise WorkspaceError(f"Failed to delete workspace after retries: {repo_path}")

    def clone_repo(self, repo_url: str, job_id: str) -> Path:
        if not repo_url or repo_url.startswith("-"):
            raise WorkspaceError(f"Invalid repository URL: {repo_url}")

        repo_path = self.create_workspace(job_id)

        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(repo_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300,
            )

            logger.info(f"Repo cloned: {repo_url}")
            return repo_path

        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
            logger.error(f"Failed to clone repo: {stderr}")
            self.delete_workspace(job_id)
            raise WorkspaceError(f"Failed to clone repository {repo_url}") from e
        except Exception as exc:
            self.delete_workspace(job_id)
            raise WorkspaceError(f"Unexpected clone failure for repository {repo_url}: {exc}") from exc

    def list_files(self, job_id: str):
        repo_path = self.get_repo_path(job_id)

        file_paths = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                file_paths.append(os.path.join(root, file))

        return file_paths

    def read_file(self, file_path: str) -> str:
        try:
            root_resolved = self.base_path.resolve()
            requested_path = Path(file_path).resolve()

            requested_path.relative_to(root_resolved)

            with open(requested_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except ValueError as exc:
            raise WorkspaceError(f"Invalid file path outside workspace: {file_path}") from exc
        except Exception as e:
            raise WorkspaceError(f"Error reading file {file_path}: {e}") from e

    def cleanup(self, job_id: str):
        self.delete_workspace(job_id)

    def cleanup_stale_workspaces(self):
        if not self.base_path.exists():
            return

        for folder in self.base_path.iterdir():
            if folder.is_dir():
                try:
                    shutil.rmtree(folder, onerror=handle_remove_readonly)
                    logger.info(f"Removed stale workspace: {folder}")
                except Exception as exc:
                    raise WorkspaceError(f"Failed to cleanup stale workspace {folder}: {exc}") from exc
