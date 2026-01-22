"""
Path security utilities for preventing path traversal attacks
"""
import os
from pathlib import Path
from typing import List, Optional

from app.core.exceptions import PathTraversalError, ValidationError


class PathValidator:
    """
    Secure path validation utilities to prevent path traversal attacks

    Usage:
        validator = PathValidator(allowed_bases=["/uploads", "/output"])
        safe_path = validator.validate_path(user_input)
    """

    DEFAULT_ALLOWED_BASES: List[str] = []

    def __init__(self, allowed_bases: Optional[List[str]] = None):
        """
        Initialize path validator with allowed base directories

        Args:
            allowed_bases: List of base paths that are allowed to be accessed.
                          If None, uses DEFAULT_ALLOWED_BASES (empty by default).
        """
        self.allowed_bases = [
            os.path.abspath(p) for p in (allowed_bases or self.DEFAULT_ALLOWED_BASES)
        ]

    def validate_path(
        self,
        path: str,
        must_exist: bool = False,
        allow_symlinks: bool = False,
    ) -> str:
        """
        Validate and normalize a path

        Args:
            path: Path to validate
            must_exist: Whether the path must exist
            allow_symlinks: Whether to allow symlinks that point outside allowed bases

        Returns:
            Normalized absolute path

        Raises:
            PathTraversalError: If path traversal detected
            ValidationError: If path doesn't exist when required
        """
        if not path or not path.strip():
            raise ValidationError("Path cannot be empty")

        # Expand user directory
        path = os.path.expanduser(path)

        # Get absolute path (resolves .. and . components)
        abs_path = os.path.abspath(path)

        # Check for path traversal - path must be within allowed bases
        if not self._is_allowed(abs_path):
            raise PathTraversalError(path)

        # Check existence if required
        if must_exist and not os.path.exists(abs_path):
            raise ValidationError(f"Path does not exist: {path}")

        # Check symlink targets if symlinks not allowed
        if not allow_symlinks and os.path.islink(abs_path):
            real_path = os.path.realpath(abs_path)
            if not self._is_allowed(real_path):
                raise PathTraversalError(f"Symlink target: {path}")

        return abs_path

    def _is_allowed(self, abs_path: str) -> bool:
        """
        Check if path is within allowed bases

        Args:
            abs_path: Absolute path to check

        Returns:
            True if path is within allowed bases
        """
        if not self.allowed_bases:
            # If no bases specified, all paths are allowed
            # This is unsafe but maintains backward compatibility
            return True

        return any(
            abs_path.startswith(base + os.sep) or abs_path == base
            for base in self.allowed_bases
        )

    def safe_join(self, base: str, *paths: str) -> str:
        """
        Safely join paths, preventing traversal attacks

        Args:
            base: Base directory
            *paths: Path components to join

        Returns:
            Safe absolute path

        Raises:
            PathTraversalError: If joined path escapes base directory
        """
        base = os.path.abspath(base)
        result = os.path.abspath(os.path.join(base, *paths))

        # Check if result is within base
        if not result.startswith(base + os.sep) and result != base:
            raise PathTraversalError(os.path.join(*paths))

        return result

    def add_allowed_base(self, base_path: str) -> None:
        """
        Add an allowed base directory

        Args:
            base_path: Path to add as allowed base
        """
        abs_path = os.path.abspath(os.path.expanduser(base_path))
        if abs_path not in self.allowed_bases:
            self.allowed_bases.append(abs_path)
