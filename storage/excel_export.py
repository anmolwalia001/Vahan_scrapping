# storage/excel_export.py
"""
Excel export utilities for managing and processing downloaded Excel files
"""

import os
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import json

logger = logging.getLogger("app.storage.excel_export")


class ExcelExporter:
    """Handles Excel file operations for the Vahan extraction system"""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls']
        logger.info("Excel exporter initialized")
    
    def validate_excel_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate Excel file and return metadata
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary with validation results and metadata
        """
        validation_result = {
            "is_valid": False,
            "file_path": file_path,
            "file_size_mb": 0,
            "sheet_count": 0,
            "total_rows": 0,
            "total_columns": 0,
            "sheet_names": [],
            "has_data": False,
            "error": None
        }
        
        try:
            if not os.path.exists(file_path):
                validation_result["error"] = "File does not exist"
                return validation_result
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                validation_result["error"] = f"Unsupported format: {file_ext}"
                return validation_result
            
            # Get file size
            file_size = os.path.getsize(file_path)
            validation_result["file_size_mb"] = round(file_size / (1024 * 1024), 2)
            
            if file_size == 0:
                validation_result["error"] = "File is empty (0 bytes)"
                return validation_result
            
            # Try to read with pandas
            try:
                # Get all sheet names first
                excel_file = pd.ExcelFile(file_path)
                validation_result["sheet_names"] = excel_file.sheet_names
                validation_result["sheet_count"] = len(excel_file.sheet_names)
                
                # Read first sheet to check data
                if excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=0)
                    validation_result["total_rows"] = len(df)
                    validation_result["total_columns"] = len(df.columns)
                    validation_result["has_data"] = not df.empty
                
                validation_result["is_valid"] = True
                logger.debug(f"Excel validation successful: {file_path}")
                
            except Exception as e:
                validation_result["error"] = f"Failed to read Excel file: {str(e)}"
                logger.error(f"Excel validation failed for {file_path}: {e}")
            
        except Exception as e:
            validation_result["error"] = f"Validation error: {str(e)}"
            logger.error(f"Excel validation error for {file_path}: {e}")
        
        return validation_result
    
    def read_excel_data(self, file_path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Read Excel file and return DataFrame
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet to read (None = first sheet)
            
        Returns:
            DataFrame or None if failed
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.debug(f"Successfully read Excel file: {file_path}")
            return df
        except Exception as e:
            logger.error(f"Failed to read Excel file {file_path}: {e}")
            return None
    
    def get_excel_summary(self, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of Excel file contents
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary with file summary
        """
        summary = {
            "file_info": {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size_mb": 0,
                "created_time": None,
                "modified_time": None
            },
            "sheets": [],
            "total_data_rows": 0,
            "is_vahan_data": False,
            "extraction_metadata": {}
        }
        
        try:
            # File info
            stat = os.stat(file_path)
            summary["file_info"]["size_mb"] = round(stat.st_size / (1024 * 1024), 2)
            summary["file_info"]["created_time"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            summary["file_info"]["modified_time"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Excel content analysis
            excel_file = pd.ExcelFile(file_path)
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    sheet_info = {
                        "name": sheet_name,
                        "rows": len(df),
                        "columns": len(df.columns),
                        "column_names": df.columns.tolist(),
                        "has_data": not df.empty,
                        "sample_data": {}
                    }
                    
                    # Add sample data (first 3 rows)
                    if not df.empty and len(df) > 0:
                        sample_rows = min(3, len(df))
                        sheet_info["sample_data"] = df.head(sample_rows).to_dict('records')
                        summary["total_data_rows"] += len(df)
                    
                    # Check if this looks like Vahan data
                    if self._is_vahan_data(df):
                        summary["is_vahan_data"] = True
                        summary["extraction_metadata"] = self._extract_vahan_metadata(df, file_path)
                    
                    summary["sheets"].append(sheet_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze sheet {sheet_name}: {e}")
                    summary["sheets"].append({
                        "name": sheet_name,
                        "error": str(e)
                    })
            
        except Exception as e:
            logger.error(f"Failed to create Excel summary for {file_path}: {e}")
            summary["error"] = str(e)
        
        return summary
    
    def create_consolidated_report(self, excel_files: List[str], output_path: str) -> bool:
        """
        Create consolidated report from multiple Excel files
        
        Args:
            excel_files: List of Excel file paths
            output_path: Path for consolidated report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Creating consolidated report from {len(excel_files)} files")
            
            workbook = openpyxl.Workbook()
            workbook.remove(workbook.active)  # Remove default sheet
            
            # Create summary sheet
            summary_sheet = workbook.create_sheet("Summary", 0)
            self._create_summary_sheet(summary_sheet, excel_files)
            
            # Process each Excel file
            consolidated_data = []
            file_errors = []
            
            for file_path in excel_files:
                try:
                    df = self.read_excel_data(file_path)
                    if df is not None and not df.empty:
                        # Add metadata columns
                        df['source_file'] = os.path.basename(file_path)
                        df['extraction_date'] = datetime.now().strftime('%Y-%m-%d')
                        
                        consolidated_data.append(df)
                        logger.debug(f"Added data from {file_path}: {len(df)} rows")
                    else:
                        file_errors.append(f"No data in {file_path}")
                        
                except Exception as e:
                    file_errors.append(f"Error reading {file_path}: {str(e)}")
                    logger.error(f"Error processing {file_path}: {e}")
            
            # Create consolidated data sheet
            if consolidated_data:
                combined_df = pd.concat(consolidated_data, ignore_index=True)
                
                # Write to Excel with formatting
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    # Write consolidated data
                    combined_df.to_excel(writer, sheet_name='Consolidated_Data', index=False)
                    
                    # Write summary
                    summary_data = {
                        'Total_Files': [len(excel_files)],
                        'Successful_Files': [len(consolidated_data)],
                        'Failed_Files': [len(file_errors)],
                        'Total_Records': [len(combined_df)],
                        'Generation_Time': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Report_Summary', index=False)
                    
                    # Write errors if any
                    if file_errors:
                        pd.DataFrame({'Errors': file_errors}).to_excel(writer, sheet_name='Errors', index=False)
                
                logger.info(f"Consolidated report created: {output_path}")
                logger.info(f"Total records: {len(combined_df)} from {len(consolidated_data)} files")
                return True
            
            else:
                logger.error("No valid data found in any Excel files")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create consolidated report: {e}")
            return False
    
    def export_extraction_summary(self, extraction_results: Dict, output_path: str) -> bool:
        """
        Export extraction results summary to Excel
        
        Args:
            extraction_results: Results from extraction service
            output_path: Path for summary Excel file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Exporting extraction summary to: {output_path}")
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Overall summary
                overall_stats = extraction_results.get('overall_stats', {})
                summary_data = []
                for key, value in overall_stats.items():
                    summary_data.append({'Metric': key.replace('_', ' ').title(), 'Value': value})
                
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Overall_Summary', index=False)
                
                # State results
                state_results = extraction_results.get('state_results', [])
                if state_results:
                    df_states = pd.DataFrame(state_results)
                    df_states.to_excel(writer, sheet_name='State_Results', index=False)
                
                # Job info
                job_info = extraction_results.get('job_info', {})
                if job_info:
                    job_data = []
                    for key, value in job_info.items():
                        if key != 'config':  # Handle config separately
                            job_data.append({'Parameter': key.replace('_', ' ').title(), 'Value': value})
                    
                    pd.DataFrame(job_data).to_excel(writer, sheet_name='Job_Info', index=False)
                    
                    # Configuration
                    config = job_info.get('config', {})
                    if config:
                        config_data = []
                        for key, value in config.items():
                            config_data.append({'Setting': key.replace('_', ' ').title(), 'Value': value})
                        
                        pd.DataFrame(config_data).to_excel(writer, sheet_name='Configuration', index=False)
            
            logger.info(f"Extraction summary exported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export extraction summary: {e}")
            return False
    
    def analyze_extraction_directory(self, extraction_dir: str) -> Dict[str, Any]:
        """
        Analyze all Excel files in an extraction directory
        
        Args:
            extraction_dir: Path to extraction directory
            
        Returns:
            Analysis summary
        """
        analysis = {
            "directory": extraction_dir,
            "analysis_time": datetime.now().isoformat(),
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "total_size_mb": 0,
            "total_records": 0,
            "files": [],
            "states": {},
            "rtos": {}
        }
        
        try:
            # Find all Excel files
            excel_files = []
            for root, dirs, files in os.walk(extraction_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.supported_formats):
                        excel_files.append(os.path.join(root, file))
            
            analysis["total_files"] = len(excel_files)
            
            # Analyze each file
            for file_path in excel_files:
                file_analysis = self.validate_excel_file(file_path)
                file_summary = self.get_excel_summary(file_path)
                
                combined_info = {**file_analysis, **file_summary}
                analysis["files"].append(combined_info)
                
                if file_analysis["is_valid"]:
                    analysis["valid_files"] += 1
                    analysis["total_size_mb"] += file_analysis["file_size_mb"]
                    analysis["total_records"] += file_analysis["total_rows"]
                    
                    # Extract state/RTO info from filename or metadata
                    self._update_state_rto_stats(analysis, file_path, file_summary)
                else:
                    analysis["invalid_files"] += 1
            
            logger.info(f"Analyzed {len(excel_files)} Excel files in {extraction_dir}")
            
        except Exception as e:
            logger.error(f"Failed to analyze extraction directory {extraction_dir}: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    def _is_vahan_data(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame contains Vahan data based on column patterns"""
        if df.empty:
            return False
        
        vahan_indicators = [
            'maker', 'state', 'rto', 'vehicle', 'registration',
            'fuel', 'class', 'category', 'month', 'year'
        ]
        
        column_names = [col.lower() for col in df.columns]
        matches = sum(1 for indicator in vahan_indicators 
                     if any(indicator in col for col in column_names))
        
        return matches >= 3  # At least 3 Vahan-related columns
    
    def _extract_vahan_metadata(self, df: pd.DataFrame, file_path: str) -> Dict:
        """Extract Vahan-specific metadata from DataFrame"""
        metadata = {
            "extracted_from": os.path.basename(file_path),
            "record_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist()
        }
        
        # Try to extract state/RTO from filename
        filename = os.path.basename(file_path).upper()
        
        # Common RTO code patterns
        import re
        rto_match = re.search(r'([A-Z]{2}\d{1,3})', filename)
        if rto_match:
            metadata["rto_code"] = rto_match.group(1)
        
        # State code patterns
        state_match = re.search(r'^([A-Z]{2})_', filename)
        if state_match:
            metadata["state_code"] = state_match.group(1)
        
        return metadata
    
    def _update_state_rto_stats(self, analysis: Dict, file_path: str, file_summary: Dict):
        """Update state and RTO statistics in analysis"""
        filename = os.path.basename(file_path)
        
        # Extract state from filename or metadata
        state_code = None
        rto_code = None
        
        if file_summary.get("extraction_metadata"):
            metadata = file_summary["extraction_metadata"]
            state_code = metadata.get("state_code")
            rto_code = metadata.get("rto_code")
        
        if state_code:
            if state_code not in analysis["states"]:
                analysis["states"][state_code] = {
                    "file_count": 0,
                    "total_records": 0,
                    "rtos": []
                }
            
            analysis["states"][state_code]["file_count"] += 1
            analysis["states"][state_code]["total_records"] += file_summary.get("total_data_rows", 0)
            
            if rto_code and rto_code not in analysis["states"][state_code]["rtos"]:
                analysis["states"][state_code]["rtos"].append(rto_code)
        
        if rto_code:
            if rto_code not in analysis["rtos"]:
                analysis["rtos"][rto_code] = {
                    "file_count": 0,
                    "total_records": 0
                }
            
            analysis["rtos"][rto_code]["file_count"] += 1
            analysis["rtos"][rto_code]["total_records"] += file_summary.get("total_data_rows", 0)
    
    def _create_summary_sheet(self, worksheet, excel_files: List[str]):
        """Create formatted summary sheet"""
        # Headers
        headers = ['File Name', 'Size (MB)', 'Status', 'Records', 'Sheets']
        for col, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # File data
        row = 2
        for file_path in excel_files:
            validation = self.validate_excel_file(file_path)
            
            worksheet.cell(row=row, column=1, value=os.path.basename(file_path))
            worksheet.cell(row=row, column=2, value=validation["file_size_mb"])
            worksheet.cell(row=row, column=3, value="Valid" if validation["is_valid"] else "Invalid")
            worksheet.cell(row=row, column=4, value=validation["total_rows"])
            worksheet.cell(row=row, column=5, value=validation["sheet_count"])
            
            row += 1


# Utility functions
def batch_validate_excel_files(directory: str) -> Dict[str, Any]:
    """
    Validate all Excel files in a directory
    
    Args:
        directory: Directory to scan for Excel files
        
    Returns:
        Validation summary
    """
    exporter = ExcelExporter()
    
    excel_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in ['.xlsx', '.xls']):
                excel_files.append(os.path.join(root, file))
    
    results = {
        "directory": directory,
        "total_files": len(excel_files),
        "valid_files": 0,
        "invalid_files": 0,
        "files": []
    }
    
    for file_path in excel_files:
        validation = exporter.validate_excel_file(file_path)
        results["files"].append(validation)
        
        if validation["is_valid"]:
            results["valid_files"] += 1
        else:
            results["invalid_files"] += 1
    
    return results


def create_extraction_report(extraction_dir: str, output_file: str = None) -> str:
    """
    Create comprehensive extraction report
    
    Args:
        extraction_dir: Directory containing extraction results
        output_file: Output Excel file path (optional)
        
    Returns:
        Path to created report file
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(extraction_dir, f"extraction_report_{timestamp}.xlsx")
    
    exporter = ExcelExporter()
    analysis = exporter.analyze_extraction_directory(extraction_dir)
    
    # Save analysis as JSON first
    json_report = os.path.join(extraction_dir, "extraction_analysis.json")
    with open(json_report, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    # Create Excel report
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Summary
        summary_data = {
            'Total Files': [analysis['total_files']],
            'Valid Files': [analysis['valid_files']],
            'Invalid Files': [analysis['invalid_files']],
            'Total Size (MB)': [analysis['total_size_mb']],
            'Total Records': [analysis['total_records']],
            'Analysis Date': [analysis['analysis_time']]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # File details
        if analysis['files']:
            files_df = pd.DataFrame(analysis['files'])
            files_df.to_excel(writer, sheet_name='File_Details', index=False)
        
        # State summary
        if analysis['states']:
            state_data = []
            for state_code, data in analysis['states'].items():
                state_data.append({
                    'State': state_code,
                    'Files': data['file_count'],
                    'Records': data['total_records'],
                    'RTOs': len(data['rtos'])
                })
            pd.DataFrame(state_data).to_excel(writer, sheet_name='States', index=False)
    
    logger.info(f"Extraction report created: {output_file}")
    return output_file