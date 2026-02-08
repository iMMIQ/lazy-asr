"""
Test to reproduce the scan bug where mp4 files are not found.

The bug occurred because:
1. config.SCAN_FILE_EXTENSIONS was an empty list []
2. _find_media_files() used extension filtering with the empty list
3. No files matched the empty extension list, so scan failed

FIX: _find_media_files now uses is_media_file() from file_type.py,
     which detects media files by content (magic bytes), consistent
     with /scan/browse and /scan/path-info APIs.
"""

import os
import tempfile
import unittest

# Add the backend directory to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.services.scan_service import ScanService


def create_minimal_mp4(path):
    """Create a minimal valid MP4 file with proper magic bytes"""
    # Minimal MP4 structure: ftyp box + mdat box
    # This is enough for filetype.guess() to detect as video/mp4
    with open(path, 'wb') as f:
        # ftyp box (box header: size=32, type='ftyp')
        f.write(b'\x00\x00\x00\x20')  # box size (32 bytes)
        f.write(b'ftyp')              # box type
        f.write(b'isom')              # major brand
        f.write(b'\x00\x00\x00\x00')  # minor version
        f.write(b'isomiso2avc1mp41')  # compatible brands
        # Empty mdat box (minimal data box)
        f.write(b'\x00\x00\x00\x08')  # box size (8 bytes)
        f.write(b'mdat')              # box type


def create_minimal_mp3(path):
    """Create a minimal valid MP3 file with proper magic bytes"""
    with open(path, 'wb') as f:
        # ID3v2 header
        f.write(b'ID3')               # ID3 identifier
        f.write(b'\x04\x00')          # Version 2.4
        f.write(b'\x00')              # Flags
        f.write(b'\x00\x00\x00\x00')  # Size (placeholder)
        # Add some actual MP3 frame data
        # MPEG Version 1, Layer III, 128kbps, 44100Hz
        f.write(b'\xff\xfb\x90\x00')  # MP3 frame header
        f.write(b'\x00' * 100)        # Some padding


class TestScanBug(unittest.TestCase):
    """Test case to reproduce and verify fix for the scan bug"""

    def setUp(self):
        """Set up test fixtures"""
        self.scan_service = ScanService()
        # Create a temporary directory with test media files
        self.temp_dir = tempfile.mkdtemp()
        self.test_mp4 = os.path.join(self.temp_dir, "test_video.mp4")
        self.test_mp3 = os.path.join(self.temp_dir, "test_audio.mp3")
        self.test_txt = os.path.join(self.temp_dir, "test.txt")

        # Create test files
        create_minimal_mp4(self.test_mp4)
        create_minimal_mp3(self.test_mp3)
        with open(self.test_txt, 'w') as f:
            f.write("Not a media file")

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_scan_file_extensions_is_empty(self):
        """Verify SCAN_FILE_EXTENSIONS is empty (by design)"""
        print(f"\nSCAN_FILE_EXTENSIONS = {settings.SCAN_FILE_EXTENSIONS}")
        self.assertEqual(settings.SCAN_FILE_EXTENSIONS, [],
                        "SCAN_FILE_EXTENSIONS is empty - by design, using filetype detection")

    def test_find_media_files_detects_mp4(self):
        """Test that _find_media_files detects MP4 files by content (not extension)"""
        media_files = self.scan_service._find_media_files(
            path=self.temp_dir,
            recursive=False,
            max_files=100
        )
        print(f"\nFiles found: {[os.path.basename(f) for f in media_files]}")
        self.assertIn(self.test_mp4, media_files,
                      "MP4 file should be detected by content")

    def test_find_media_files_detects_mp3(self):
        """Test that _find_media_files detects MP3 files by content (not extension)"""
        media_files = self.scan_service._find_media_files(
            path=self.temp_dir,
            recursive=False,
            max_files=100
        )
        print(f"\nFiles found: {[os.path.basename(f) for f in media_files]}")
        self.assertIn(self.test_mp3, media_files,
                      "MP3 file should be detected by content")

    def test_find_media_files_ignores_non_media(self):
        """Test that _find_media_files ignores non-media files"""
        media_files = self.scan_service._find_media_files(
            path=self.temp_dir,
            recursive=False,
            max_files=100
        )
        print(f"\nFiles found: {[os.path.basename(f) for f in media_files]}")
        self.assertNotIn(self.test_txt, media_files,
                         "Non-media files should be ignored")

    def test_filetype_detection_consistency(self):
        """Test that _find_media_files uses filetype detection consistently"""
        from app.utils.file_type import is_media_file

        # All files detected by is_media_file should be found by _find_media_files
        expected_media_files = []
        for entry in os.listdir(self.temp_dir):
            entry_path = os.path.join(self.temp_dir, entry)
            if os.path.isfile(entry_path) and is_media_file(entry_path):
                expected_media_files.append(entry_path)

        found_media_files = self.scan_service._find_media_files(
            path=self.temp_dir,
            recursive=False,
            max_files=100
        )

        # Convert to sets for comparison
        expected_set = set(expected_media_files)
        found_set = set(found_media_files)

        print(f"\nExpected by is_media_file: {expected_set}")
        print(f"Found by _find_media_files: {found_set}")

        self.assertEqual(expected_set, found_set,
                         "Consistency: Both methods should find the same files")

    def test_find_media_files_respects_max_files(self):
        """Test that _find_media_files respects max_files limit"""
        # Create more media files than max_files
        for i in range(10):
            mp4_path = os.path.join(self.temp_dir, f"video_{i}.mp4")
            create_minimal_mp4(mp4_path)

        media_files = self.scan_service._find_media_files(
            path=self.temp_dir,
            recursive=False,
            max_files=5
        )

        print(f"\nMax files=5, found: {len(media_files)}")
        self.assertLessEqual(len(media_files), 5,
                            "Should respect max_files limit")

    def test_find_media_files_recursive(self):
        """Test recursive scanning"""
        # Create subdirectory with media file
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir)
        sub_mp4 = os.path.join(sub_dir, "sub_video.mp4")
        create_minimal_mp4(sub_mp4)

        # Non-recursive should only find files in root
        non_recursive = self.scan_service._find_media_files(
            path=self.temp_dir,
            recursive=False,
            max_files=100
        )
        self.assertNotIn(sub_mp4, non_recursive,
                         "Non-recursive should not find files in subdirs")

        # Recursive should find all files
        recursive = self.scan_service._find_media_files(
            path=self.temp_dir,
            recursive=True,
            max_files=100
        )
        self.assertIn(sub_mp4, recursive,
                      "Recursive should find files in subdirs")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
