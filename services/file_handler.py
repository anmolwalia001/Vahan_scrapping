# services/file_handler.py
"""
File handling service for managing downloaded Excel files and organizing results
"""

import os
import shutil
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import hashlib

logger = logging.getLogger("app.services.file_handler")


class FileHandler:
    """Handles file operations for the extraction service"""
    
    def __init__(self):
        self.base_output_dir = "result"
        self.ensure_base_directories()
    
    def ensure_base_directories(self):
        """Ensure base directories exist"""
        directories = [
            self.base_output_dir,
            os.path.join(self.base_output_dir, "temp"),
            os.path.join(self.base_output_dir, "archive"),
            "logs"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_extraction_directory(self, extraction_name: str) -> str:
        """Create a new extraction directory with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"{extraction_name}_{timestamp}"
        full_path = os.path.join(self.base_output_dir, dir_name)
        
        os.makedirs(full_path, exist_ok=True)
        
        # Create subdirectories
        subdirs = ["states", "summaries", "logs", "temp_downloads"]
        for subdir in subdirs:
            os.makedirs(os.path.join(full_path, subdir), exist_ok=True)
        
        logger.info(f"Created extraction directory: {full_path}")
        return full_path
    
    def create_state_directory(self, extraction_dir: str, state_code: str, state_name: str) -> str:
        """Create directory for a specific state"""
        safe_state_name = self._sanitize_filename(state_name)
        state_dir_name = f"{state_code}_{safe_state_name}"
        state_path = os.path.join(extraction_dir, "states", state_dir_name)
        
        os.makedirs(state_path, exist_ok=True)
        
        # Create RTO subdirectory
        os.makedirs(os.path.join(state_path, "rtos"), exist_ok=True)
        
        logger.debug(f"Created state directory: {state_path}")
        return state_path
    
    def move_downloaded_file(self, temp_file_path: str, destination_dir: str, new_filename: str) -> str:
        """Move downloaded file from temp location to final destination"""
        if not os.path.exists(temp_file_path):
            raise FileNotFoundError(f"Temp file not found: {temp_file_path}")
        
        destination_path = os.path.join(destination_dir, new_filename)
        
        # Ensure destination directory exists
        os.makedirs(destination_dir, exist_ok=True)
        
        # Move the file
        shutil.move(temp_file_path, destination_path)
        
        # Verify file was moved successfully
        if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
            logger.debug(f"Successfully moved file to: {destination_path}")
            return destination_path
        else:
            raise Exception(f"Failed to move file to: {destination_path}")
    
    def copy_file(self, source_path: str, destination_dir: str, new_filename: str = None) -> str:
        """Copy file to destination directory"""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if new_filename is None:
            new_filename = os.path.basename(source_path)
        
        destination_path = os.path.join(destination_dir, new_filename)
        
        # Ensure destination directory exists
        os.makedirs(destination_dir, exist_ok=True)
        
        # Copy the file
        shutil.copy2(source_path, destination_path)
        
        logger.debug(f"Copied file to: {destination_path}")
        return destination_path
    
    def save_json_summary(self, data: Dict, file_path: str):
        """Save dictionary as JSON file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.debug(f"Saved JSON summary to: {file_path}")
    
    def load_json_summary(self, file_path: str) -> Dict:
        """Load JSON file as dictionary"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.debug(f"Loaded JSON summary from: {file_path}")
        return data
    
    def save_progress_file(self, extraction_dir: str, state_code: str, processed_rtos: List[str]):
        """Save progress file for resuming extraction"""
        progress_data = {
            "state_code": state_code,
            "processed_rtos": processed_rtos,
            "last_updated": datetime.now().isoformat()
        }
        
        progress_file = os.path.join(extraction_dir, f"progress_{state_code}.json")
        self.save_json_summary(progress_data, progress_file)
        
        logger.debug(f"Saved progress for state {state_code}")
    
    def load_progress_file(self, extraction_dir: str, state_code: str) -> List[str]:
        """Load progress file to resume extraction"""
        progress_file = os.path.join(extraction_dir, f"progress_{state_code}.json")
        
        if not os.path.exists(progress_file):
            return []
        
        try:
            progress_data = self.load_json_summary(progress_file)
            processed_rtos = progress_data.get("processed_rtos", [])
            logger.debug(f"Loaded progress for state {state_code}: {len(processed_rtos)} RTOs processed")
            return processed_rtos
        except Exception as e:
            logger.error(f"Error loading progress file for {state_code}: {e}")
            return []
    
    def cleanup_temp_files(self, extraction_dir: str):
        """Clean up temporary files"""
        temp_dir = os.path.join(extraction_dir, "temp_downloads")
        
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                try:
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp file {file}: {e}")
        
        logger.debug("Cleaned up temporary files")
    
    def archive_extraction(self, extraction_dir: str, archive_name: str = None) -> str:
        """Archive completed extraction directory"""
        if archive_name is None:
            archive_name = f"archived_{os.path.basename(extraction_dir)}"
        
        archive_dir = os.path.join(self.base_output_dir, "archive")
        archive_path = os.path.join(archive_dir, archive_name)
        
        # Create archive directory
        shutil.copytree(extraction_dir, archive_path)
        
        # Remove original directory
        shutil.rmtree(extraction_dir)
        
        logger.info(f"Archived extraction to: {archive_path}")
        return archive_path
    
    def get_file_info(self, file_path: str) -> Dict:
        """Get information about a file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = os.stat(file_path)
        
        return {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "file_hash": self._calculate_file_hash(file_path)
        }
    
    def get_directory_size(self, directory_path: str) -> Dict:
        """Get size information for a directory"""
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        total_size = 0
        file_count = 0
        
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                    file_count += 1
                except (OSError, IOError):
                    pass
        
        return {
            "directory_path": directory_path,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count
        }
    
    def list_extraction_results(self) -> List[Dict]:
        """List all available extraction results"""
        results = []
        
        if not os.path.exists(self.base_output_dir):
            return results
        
        for item in os.listdir(self.base_output_dir):
            item_path = os.path.join(self.base_output_dir, item)
            
            if os.path.isdir(item_path) and not item.startswith('.'):
                # Check if it looks like an extraction directory
                if any(subdir in os.listdir(item_path) for subdir in ['states', 'summaries']):
                    try:
                        dir_info = self.get_directory_size(item_path)
                        results.append({
                            "name": item,
                            "path": item_path,
                            "size_mb": dir_info["total_size_mb"],
                            "file_count": dir_info["file_count"],
                            "created_time": datetime.fromtimestamp(
                                os.path.getctime(item_path)
                            ).isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"Could not get info for {item}: {e}")
        
        # Sort by creation time, newest first
        results.sort(key=lambda x: x["created_time"], reverse=True)
        return results
    
    def validate_excel_file(self, file_path: str) -> bool:
        """Validate that a file is a proper Excel file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Check file extension
            if not file_path.lower().endswith(('.xlsx', '.xls')):
                return False
            
            # Check file size (should be > 0)
            if os.path.getsize(file_path) == 0:
                return False
            
            # Try to read with pandas (basic validation)
            try:
                import pandas as pd
                pd.read_excel(file_path, nrows=1)
                return True
            except Exception:
                # If pandas is not available or file is corrupted
                return False
                
        except Exception as e:
            logger.error(f"Error validating Excel file {file_path}: {e}")
            return False
    
    def generate_file_manifest(self, extraction_dir: str) -> Dict:
        """Generate a manifest of all files in an extraction directory"""
        manifest = {
            "extraction_directory": extraction_dir,
            "generated_time": datetime.now().isoformat(),
            "files": []
        }
        
        for root, dirs, files in os.walk(extraction_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, extraction_dir)
                
                try:
                    file_info = self.get_file_info(file_path)
                    file_info["relative_path"] = relative_path
                    
                    # Add Excel-specific validation
                    if file.lower().endswith(('.xlsx', '.xls')):
                        file_info["is_valid_excel"] = self.validate_excel_file(file_path)
                    
                    manifest["files"].append(file_info)
                    
                except Exception as e:
                    logger.warning(f"Could not get info for file {file_path}: {e}")
        
        # Save manifest
        manifest_path = os.path.join(extraction_dir, "file_manifest.json")
        self.save_json_summary(manifest, manifest_path)
        
        logger.info(f"Generated file manifest: {manifest_path}")
        return manifest
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return "error"