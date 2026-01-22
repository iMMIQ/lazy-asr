"""
Path validation tests - TDD First Cycle
"""
import os
import tempfile
import pytest
from pathlib import Path


class TestPathValidator:
    """Test PathValidator for security against path traversal attacks"""

    def test_rejects_path_traversal_with_double_dots(self):
        """Should reject paths with ../ for security"""
        # This test should FAIL initially because PathValidator doesn't exist
        from app.utils.path_utils import PathValidator

        validator = PathValidator(allowed_bases=["/tmp/allowed"])

        with pytest.raises(Exception):  # PathTraversalError expected
            validator.validate_path("/tmp/allowed/../../../etc/passwd")

    def test_rejects_absolute_path_traversal(self):
        """Should reject absolute paths outside allowed bases"""
        from app.utils.path_utils import PathValidator

        validator = PathValidator(allowed_bases=["/tmp/allowed"])

        with pytest.raises(Exception):
            validator.validate_path("/etc/passwd")

    def test_accepts_valid_path_within_allowed_base(self):
        """Should accept paths within allowed base directories"""
        from app.utils.path_utils import PathValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator(allowed_bases=[tmpdir])

            # Create a test file
            test_file = os.path.join(tmpdir, "test.txt")
            Path(test_file).touch()

            # Should not raise
            result = validator.validate_path(test_file)
            assert result == os.path.abspath(test_file)

    def test_normalizes_paths(self):
        """Should normalize paths to absolute paths"""
        from app.utils.path_utils import PathValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator(allowed_bases=[tmpdir])

            # Test relative path normalization
            os.chdir(tmpdir)
            result = validator.validate_path(".")
            assert os.path.isabs(result)

    def test_rejects_symlink_traversal(self):
        """Should reject symlinks pointing outside allowed bases"""
        from app.utils.path_utils import PathValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            allowed_dir = os.path.join(tmpdir, "allowed")
            os.makedirs(allowed_dir)

            outside_dir = os.path.join(tmpdir, "outside")
            os.makedirs(outside_dir)

            # Create symlink pointing outside
            symlink_path = os.path.join(allowed_dir, "escape_link")
            os.symlink(outside_dir, symlink_path)

            validator = PathValidator(allowed_bases=[allowed_dir])

            # Should reject the symlink target
            with pytest.raises(Exception):
                validator.validate_path(symlink_path, must_exist=True)

    def test_safe_join_prevents_traversal(self):
        """safe_join should prevent path traversal"""
        from app.utils.path_utils import PathValidator

        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator(allowed_bases=[tmpdir])

            with pytest.raises(Exception):
                validator.safe_join(tmpdir, "../etc", "passwd")
