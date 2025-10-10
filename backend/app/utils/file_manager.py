import os
import shutil
from typing import List, Optional
from app.core.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """File manager responsible for cleaning up files during ASR processing"""

    def __init__(self):
        self.upload_dir = "uploads"
        self.output_dir = "output"

    def cleanup_task_files(self, task_id: str, keep_output: bool = True) -> bool:
        """
        Clean up all temporary files and uploaded files for a specific task

        Args:
            task_id: Task ID
            keep_output: Whether to keep output files

        Returns:
            Whether cleanup was successful
        """
        try:
            logger.info(f"Starting file cleanup for task {task_id}")

            # Clean up upload file directory
            upload_task_dir = os.path.join(self.upload_dir, task_id)
            if os.path.exists(upload_task_dir):
                shutil.rmtree(upload_task_dir)
                logger.info(f"Cleaned up upload file directory: {upload_task_dir}")

            # Clean up temporary files in output directory (keep final output files)
            output_task_dir = os.path.join(self.output_dir, task_id)
            if os.path.exists(output_task_dir) and not keep_output:
                # If not keeping output files, delete entire output directory
                shutil.rmtree(output_task_dir)
                logger.info(f"Cleaned up output file directory: {output_task_dir}")
            elif os.path.exists(output_task_dir):
                # If keeping output files, only delete temporary files
                self._cleanup_temp_files(output_task_dir)
                logger.info(f"Cleaned up temporary files, kept output files: {output_task_dir}")

            logger.info(f"File cleanup completed for task {task_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to clean up files for task {task_id}: {e}")
            return False

    def cleanup_by_media_path(self, media_path: str, task_id: str, keep_output: bool = True) -> bool:
        """
        Clean up files based on media file path and task ID

        Args:
            media_path: Path to the media file (e.g., uploads/{task_id}/filename)
            task_id: Task ID
            keep_output: Whether to keep output files

        Returns:
            Whether cleanup was successful
        """
        try:
            logger.info(f"Starting file cleanup for media path: {media_path}")

            # Extract task ID from media path if it's in uploads directory
            if media_path.startswith(self.upload_dir + os.sep):
                # Extract the task_id part from the path: uploads/{task_id}/filename
                relative_path = os.path.relpath(media_path, self.upload_dir)
                path_parts = relative_path.split(os.sep)
                if len(path_parts) >= 1:
                    extracted_task_id = path_parts[0]
                    upload_task_dir = os.path.join(self.upload_dir, extracted_task_id)
                    if os.path.exists(upload_task_dir):
                        shutil.rmtree(upload_task_dir)
                        logger.info(f"Cleaned up upload file directory: {upload_task_dir}")

            # Clean up temporary files in output directory (keep final output files)
            output_task_dir = os.path.join(self.output_dir, task_id)
            if os.path.exists(output_task_dir) and not keep_output:
                # If not keeping output files, delete entire output directory
                shutil.rmtree(output_task_dir)
                logger.info(f"Cleaned up output file directory: {output_task_dir}")
            elif os.path.exists(output_task_dir):
                # If keeping output files, only delete temporary files
                self._cleanup_temp_files(output_task_dir)
                logger.info(f"Cleaned up temporary files, kept output files: {output_task_dir}")

            logger.info(f"File cleanup completed for media path: {media_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to clean up files for media path {media_path}: {e}")
            return False

    def _cleanup_temp_files(self, task_output_dir: str) -> None:
        """
        Clean up temporary files in task output directory

        Args:
            task_output_dir: Task output directory path
        """
        try:
            # Clean up silero_segments directory
            segments_dir = os.path.join(task_output_dir, "silero_segments")
            if os.path.exists(segments_dir):
                shutil.rmtree(segments_dir)
                logger.info(f"Cleaned up audio segments directory: {segments_dir}")

            # Clean up processed audio files (files ending with _processed.wav)
            for filename in os.listdir(task_output_dir):
                file_path = os.path.join(task_output_dir, filename)
                if filename.endswith("_processed.wav") and os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up processed audio file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to clean up temporary files: {e}")

    def cleanup_upload_file(self, file_path: str) -> bool:
        """
        Clean up a single uploaded file

        Args:
            file_path: File path

        Returns:
            Whether cleanup was successful
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up uploaded file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to clean up uploaded file {file_path}: {e}")
            return False

    def get_task_files(self, task_id: str) -> dict:
        """
        Get all file information related to a task

        Args:
            task_id: Task ID

        Returns:
            Dictionary of file information
        """
        files_info = {"upload_files": [], "temp_files": [], "output_files": []}

        # Get upload files
        upload_task_dir = os.path.join(self.upload_dir, task_id)
        if os.path.exists(upload_task_dir):
            for root, dirs, files in os.walk(upload_task_dir):
                for file in files:
                    files_info["upload_files"].append(os.path.join(root, file))

        # Get files in output directory
        output_task_dir = os.path.join(self.output_dir, task_id)
        if os.path.exists(output_task_dir):
            for root, dirs, files in os.walk(output_task_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if "silero_segments" in file_path or file.endswith("_processed.wav"):
                        files_info["temp_files"].append(file_path)
                    elif file.endswith(('.srt', '.vtt', '.lrc', '.txt')):
                        files_info["output_files"].append(file_path)

        return files_info
