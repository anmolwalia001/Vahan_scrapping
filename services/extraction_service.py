# # services/extraction_service.py
# """
# Main extraction service that orchestrates the data extraction process
# """

# import logging
# import time
# import os
# from datetime import datetime, timedelta
# from typing import List, Dict, Optional, Tuple
# from dataclasses import dataclass
# from enum import Enum
# from selenium.webdriver.common.by import By
# from extractor.extract_states import StateExtractor, StateData
# from extractor.extract_all_rto import RTOExtractor, RTOData
# from extractor.extract_axis import AxisExtractor, AxisFilterData
# from extractor.extract_vehicle_filter import VehicleFilterExtractor, VehicleFilterData
# from scrapper.browser import VahanBrowser
# from storage.excel_export import ExcelExporter
# from services.file_handler import FileHandler
# from utils.helpers import sanitize_filename
# from db.session import SessionLocal
# from random import uniform
# from db.models import ExtractionJob, ExtractionResult

# logger = logging.getLogger("app.services.extraction")


# class ExtractionStatus(Enum):
#     """Status of extraction job"""
#     PENDING = "pending"
#     IN_PROGRESS = "in_progress"
#     COMPLETED = "completed"
#     FAILED = "failed"
#     PAUSED = "paused"


# @dataclass
# class ExtractionConfig:
#     """Configuration for extraction job"""
#     y_axis: str = "Maker"
#     x_axis: str = "Month Wise"
#     apply_vehicle_filter: bool = True
#     vehicle_filter_categories: List[str] = None
#     state_delay_minutes: int = 5
#     rto_delay_seconds: int = 2
#     state_delay_jitter_minutes: float = 1.0
#     rto_delay_jitter_seconds: float = 3.0
#     max_retries: int = 3
#     output_directory: str = None
    
#     def __post_init__(self):
#         if self.vehicle_filter_categories is None:
#             self.vehicle_filter_categories = ["MOTOR CAR", "MOTOR CAB", "ELECTRIC(BOV)", "PURE EV"]
        
#         if self.output_directory is None:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             self.output_directory = f"vahan_extraction_{timestamp}"


# @dataclass
# class StateExtractionResult:
#     """Result of state extraction"""
#     state: StateData
#     total_rtos: int
#     processed_rtos: int
#     successful_downloads: int
#     failed_downloads: int
#     skipped_rtos: int
#     excel_files: List[str]
#     errors: List[str]
#     start_time: datetime
#     end_time: Optional[datetime]
#     duration_minutes: float


# class ExtractionService:
#     """Main service for orchestrating data extraction"""
    
#     def __init__(self, config: ExtractionConfig = None):
#         self.config = config or ExtractionConfig()
#         self.state_extractor = StateExtractor()
#         self.rto_extractor = RTOExtractor()
#         self.axis_extractor = AxisExtractor()
#         self.vehicle_extractor = VehicleFilterExtractor()
#         self.file_handler = FileHandler()
#         self.excel_exporter = ExcelExporter()
        
#         # Initialize browser (will be created when needed)
#         self.browser = None
        
#         # Job tracking
#         self.current_job = None
#         self.extraction_results = []
        
#         logger.info(f"Extraction service initialized with config: {self.config}")
    
#     def start_full_extraction(self, specific_states: List[str] = None) -> Dict:
#         """
#         Start full extraction process for all active states
        
#         Args:
#             specific_states: List of state codes to process (None = all active states)
        
#         Returns:
#             Dictionary with job summary
#         """
#         start_time = datetime.now()
#         logger.info(f"Starting full extraction at {start_time}")
        
#         try:
#             # Get active states from database
#             active_states = self.state_extractor.extract_active_states()
            
#             if specific_states:
#                 # Filter to specific states
#                 active_states = [s for s in active_states if s.code in specific_states]
#                 logger.info(f"Filtering to specific states: {specific_states}")
            
#             if not active_states:
#                 raise ValueError("No active states found to process")
            
#             logger.info(f"Processing {len(active_states)} states: {[s.name for s in active_states]}")
            
#             # Create job record
#             job_id = self._create_extraction_job(active_states)
            
#             # Setup output directory
#             output_dir = self._setup_output_directory()
#             logger.info(f"Output directory: {output_dir}")
            
#             # Initialize browser
#             self._initialize_browser()
            
#             # Process each state
#             state_results = []
#             total_excel_files = 0
            
#             for idx, state in enumerate(active_states):
                
                
#                 try:
#                     # Extract data for this state
#                     state_result = self._process_state(state, output_dir)
#                     state_results.append(state_result)
#                     total_excel_files += state_result.successful_downloads
                    
#                     # Wait between states (except for last state)
#                     if idx < len(active_states) - 1:
#                         self._sleep_with_jitter_minutes(self.config.state_delay_minutes, self.config.state_delay_jitter_minutes)
                
#                 except Exception as e:
#                     logger.error(f"Failed to process state {state.name}: {e}")
#                     # Continue with next state
#                     continue
            
#             # Finalize job
#             end_time = datetime.now()
#             duration = (end_time - start_time).total_seconds() / 60
            
#             self._finalize_extraction_job(job_id, state_results, end_time)
            
#             # Generate summary
#             summary = self._generate_extraction_summary(state_results, start_time, end_time)
            
#             logger.info(f"\n{'='*70}")
#             logger.info("EXTRACTION COMPLETED")
#             logger.info(f"{'='*70}")
#             logger.info(f"Total Duration: {duration:.1f} minutes")
#             logger.info(f"Total Excel Files: {total_excel_files}")
#             logger.info(f"States Processed: {len(state_results)}")
            
#             return summary
            
#         except Exception as e:
#             logger.error(f"Fatal error in extraction process: {e}")
#             raise
#         finally:
#             self._cleanup_browser()
    
#     def _initialize_browser(self):
#         """Initialize the browser instance"""
#         if not self.browser:
#             self.browser = VahanBrowser()
#             self.browser.setup()

#             # 1) Read current axis labels from DB (source of truth)
#             axis_extractor = AxisExtractor()
#             labels = axis_extractor.get_current_axis_labels()
#             y_axis_from_db = labels["Y"]
#             x_axis_from_db = labels["X"]

#             # 2) Navigate and set + verify
#             if not self.browser.navigate_to_portal():
#                 raise Exception("Failed to navigate to portal")

#             if not self.browser.set_axis_and_verify(y_axis_from_db, x_axis_from_db):
#                 # FAIL FAST so you don’t run with defaults like "Vehicle Category Group"
#                 raise Exception(
#                     f"Failed to apply axes from DB. Y='{y_axis_from_db}', X='{x_axis_from_db}'"
#                 )

#             # Optionally reflect what we actually used to the config for logging
#             self.config.y_axis = y_axis_from_db
#             self.config.x_axis = x_axis_from_db
    
#     def _process_state(self, state: StateData, output_dir: str) -> StateExtractionResult:
#         """Process all RTOs for a single state"""
#         start_time = datetime.now()
        
#         # Get RTOs for this state
#         rtos = self.rto_extractor.extract_rtos_by_state_id(state.id)
#         logger.info(f"Found {len(rtos)} RTOs for {state.name}")
        
#         if not rtos:
#             logger.warning(f"No RTOs found for {state.name}")
#             return StateExtractionResult(
#                 state=state,
#                 total_rtos=0,
#                 processed_rtos=0,
#                 successful_downloads=0,
#                 failed_downloads=0,
#                 skipped_rtos=0,
#                 excel_files=[],
#                 errors=["No RTOs found"],
#                 start_time=start_time,
#                 end_time=datetime.now(),
#                 duration_minutes=0
#             )
        
#         # Create state output directory
#         state_dir = os.path.join(output_dir, sanitize_filename(f"{state.code}_{state.name}"))
#         os.makedirs(state_dir, exist_ok=True)
        
#         # Setup browser for this state
#         self._setup_browser_for_state(state)
        
#         # Process each RTO
#         excel_files = []
#         errors = []
#         successful_downloads = 0
#         failed_downloads = 0
        
#         for idx, rto in enumerate(rtos):
#             logger.info(f"\nProcessing RTO {idx+1}/{len(rtos)}: {rto.name} ({rto.code})")
            
#             try:
#                 # Extract data for this RTO
#                 rto_files = self._process_rto(rto, state_dir)
                
#                 if rto_files:
#                     excel_files.extend(rto_files)
#                     successful_downloads += len(rto_files)
#                     logger.info(f"✓ Downloaded {len(rto_files)} files for {rto.name}")
#                 else:
#                     failed_downloads += 1
#                     error_msg = f"No data found for {rto.name}"
#                     errors.append(error_msg)
#                     logger.warning(f"⚠ {error_msg}")
                
#                 # Small delay between RTOs
#                 if idx < len(rtos) - 1:
#                     self._sleep_with_jitter_seconds(self.config.rto_delay_seconds, self.config.rto_delay_jitter_seconds)
                    
#             except Exception as e:
#                 failed_downloads += 1
#                 error_msg = f"Error processing {rto.name}: {str(e)[:200]}"
#                 errors.append(error_msg)
#                 logger.error(f"✗ {error_msg}")
                
#                 # Try to recover browser
#                 try:
#                     self.browser.refresh_page()
#                     self._setup_browser_for_state(state)  # Re-setup state selection
#                 except:
#                     logger.error("Failed to recover browser, continuing...")
        
#         end_time = datetime.now()
#         duration = (end_time - start_time).total_seconds() / 60
        
#         return StateExtractionResult(
#             state=state,
#             total_rtos=len(rtos),
#             processed_rtos=len(rtos),
#             successful_downloads=successful_downloads,
#             failed_downloads=failed_downloads,
#             skipped_rtos=0,
#             excel_files=excel_files,
#             errors=errors,
#             start_time=start_time,
#             end_time=end_time,
#             duration_minutes=duration
#         )
    
#     def _process_rto(self, rto: RTOData, state_dir: str) -> List[str]:
#         """Process a single RTO and download Excel files"""
#         excel_files = []
        
#         try:
#             # Select RTO in browser
#             if not self.browser.select_rto(rto.full_text or rto.name):
#                 logger.error(f"Failed to select RTO: {rto.name}")
#                 return excel_files
            
#             # Refresh data
#             self.browser.click_refresh()
            
#             # Apply filters if configured
#             if self.config.apply_vehicle_filter:
#                 # Process each filter category set
#                 filter_sets = [
#                     (["MOTOR CAR", "MOTOR CAB"], "motor_car_cab"),
#                     (["ELECTRIC(BOV)", "PURE EV"], "ev_bov")
#                 ]
                
#                 for filter_categories, filter_suffix in filter_sets:
#                     try:
#                         # Apply filter
#                         if not self.browser.apply_vehicle_filter(filter_categories):
#                             logger.warning(f"Failed to apply filter {filter_categories} for {rto.name}")
#                             continue
                        
#                         # Check if data exists
#                         if not self.browser.check_data_exists():
#                             logger.info(f"No data found for {rto.name} with filter {filter_suffix}")
#                             continue
                        
#                         # Download Excel
#                         filename = self._generate_filename(rto, filter_suffix)
#                         if self.browser.download_excel(state_dir, filename):
#                             excel_files.append(filename)
#                             logger.info(f"Downloaded: {filename}")
                        
#                     except Exception as e:
#                         logger.error(f"Error processing filter {filter_suffix} for {rto.name}: {e}")
            
#             else:
#                 # Download without filter
#                 if self.browser.check_data_exists():
#                     filename = self._generate_filename(rto)
#                     if self.browser.download_excel(state_dir, filename):
#                         excel_files.append(filename)
#                         logger.info(f"Downloaded: {filename}")
#                 else:
#                     logger.info(f"No data found for {rto.name}")
            
#         except Exception as e:
#             logger.error(f"Error processing RTO {rto.name}: {e}")
        
#         return excel_files
    
#     def _initialize_browser(self):
#         """Initialize the browser instance"""
#         if not self.browser:
#             self.browser = VahanBrowser()
#             self.browser.setup()
            
#             # Navigate to portal and set axis
#             self.browser.navigate_to_portal()
#             self.browser.set_axis(self.config.y_axis, self.config.x_axis)
    
#     def _setup_browser_for_state(self, state: StateData):
#         """Setup browser for processing a specific state"""
#         if not self.browser:
#             self._initialize_browser()
        
#         # Select state
#         state_display_name = getattr(state, "display_name", state.name)
        
#         if not self.browser.select_state(state_display_name):
#             raise Exception(f"Failed to select state: {state_display_name}")
    
#     def _cleanup_browser(self):
#         """Clean up browser resources"""
#         if self.browser:
#             try:
#                 self.browser.quit()
#             except:
#                 pass
#             self.browser = None
    
#     def _generate_filename(self, rto: RTOData, filter_suffix: str = None) -> str:
#         """Generate filename for Excel download"""
#         safe_rto_name = sanitize_filename(rto.name)[:30]
#         axis_suffix = f"{self.config.y_axis.lower()}_{self.config.x_axis.lower().replace(' ', '_')}"
        
#         if filter_suffix:
#             axis_suffix += f"_{filter_suffix}"
        
#         if rto.code == "ALL":
#             return f"ALL_{rto.state_code}_RTOS_{axis_suffix}.xlsx"
#         else:
#             return f"{rto.code}_{safe_rto_name}_{axis_suffix}.xlsx"
    
#     def _setup_output_directory(self) -> str:
#         """Setup and return output directory path"""
#         output_dir = os.path.join("result", self.config.output_directory)
#         os.makedirs(output_dir, exist_ok=True)
        
#         # Create subdirectories
#         os.makedirs(os.path.join(output_dir, "logs"), exist_ok=True)
#         os.makedirs(os.path.join(output_dir, "summaries"), exist_ok=True)
        
#         return output_dir
    
#     def _create_extraction_job(self, states: List[StateData]) -> int:
#         """Create extraction job record in database"""
#         try:
#             with SessionLocal() as db:
#                 job = ExtractionJob(
#                     start_time=datetime.now(),
#                     status=ExtractionStatus.IN_PROGRESS.value,
#                     config={
#                         "y_axis": self.config.y_axis,
#                         "x_axis": self.config.x_axis,
#                         "apply_vehicle_filter": self.config.apply_vehicle_filter,
#                         "vehicle_filter_categories": self.config.vehicle_filter_categories,
#                         "state_count": len(states),
#                         "state_codes": [s.code for s in states]
#                     }
#                 )
                
#                 db.add(job)
#                 db.commit()
#                 db.refresh(job)
                
#                 self.current_job = job
#                 logger.info(f"Created extraction job with ID: {job.id}")
#                 return job.id
                
#         except Exception as e:
#             logger.error(f"Failed to create extraction job: {e}")
#             return None
    
#     def _finalize_extraction_job(self, job_id: int, results: List[StateExtractionResult], end_time: datetime):
#         """Finalize extraction job in database"""
#         if not job_id:
#             return
        
#         try:
#             with SessionLocal() as db:
#                 job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
#                 if job:
#                     total_files = sum(r.successful_downloads for r in results)
#                     total_errors = sum(len(r.errors) for r in results)
                    
#                     job.end_time = end_time
#                     job.status = ExtractionStatus.COMPLETED.value if total_errors == 0 else ExtractionStatus.FAILED.value
#                     job.total_files_downloaded = total_files
#                     job.total_errors = total_errors
#                     job.summary = {
#                         "states_processed": len(results),
#                         "total_rtos": sum(r.total_rtos for r in results),
#                         "successful_downloads": total_files,
#                         "failed_downloads": sum(r.failed_downloads for r in results)
#                     }
                    
#                     db.commit()
#                     logger.info(f"Finalized extraction job {job_id}")
                
#         except Exception as e:
#             logger.error(f"Failed to finalize extraction job: {e}")
    
#     def _generate_extraction_summary(self, results: List[StateExtractionResult], start_time: datetime, end_time: datetime) -> Dict:
#         """Generate summary of extraction results"""
#         total_rtos = sum(r.total_rtos for r in results)
#         total_files = sum(r.successful_downloads for r in results)
#         total_failures = sum(r.failed_downloads for r in results)
#         total_errors = sum(len(r.errors) for r in results)
        
#         duration = (end_time - start_time).total_seconds() / 60
        
#         summary = {
#             "job_info": {
#                 "start_time": start_time.isoformat(),
#                 "end_time": end_time.isoformat(),
#                 "duration_minutes": round(duration, 2),
#                 "config": {
#                     "y_axis": self.config.y_axis,
#                     "x_axis": self.config.x_axis,
#                     "vehicle_filter_applied": self.config.apply_vehicle_filter,
#                     "state_delay_minutes": self.config.state_delay_minutes
#                 }
#             },
#             "overall_stats": {
#                 "states_processed": len(results),
#                 "total_rtos": total_rtos,
#                 "excel_files_downloaded": total_files,
#                 "failed_downloads": total_failures,
#                 "total_errors": total_errors,
#                 "success_rate": round((total_files / total_rtos * 100) if total_rtos > 0 else 0, 2)
#             },
#             "state_results": []
#         }
        
#         # Add state-by-state results
#         for result in results:
#             summary["state_results"].append({
#                 "state_name": result.state.name,
#                 "state_code": result.state.code,
#                 "rtos_processed": result.processed_rtos,
#                 "files_downloaded": result.successful_downloads,
#                 "failures": result.failed_downloads,
#                 "duration_minutes": round(result.duration_minutes, 2),
#                 "success_rate": round((result.successful_downloads / result.total_rtos * 100) if result.total_rtos > 0 else 0, 2)
#             })
        
#         return summary
    
#     def _sleep_with_jitter_seconds(self, base: float, jitter: float):
#         time.sleep(max(0, base + uniform(-jitter, jitter)))

#     def _sleep_with_jitter_minutes(self, base: float, jitter: float):
#         self._sleep_with_jitter_seconds(base * 60.0, jitter * 60.0)
    
#     def pause_extraction(self):
#         """Pause the current extraction"""
#         # Implementation for pausing extraction
#         logger.info("Extraction paused")
    
#     def resume_extraction(self):
#         """Resume paused extraction"""
#         # Implementation for resuming extraction
#         logger.info("Extraction resumed")
    
#     def get_extraction_status(self) -> Dict:
#         """Get current extraction status"""
#         if self.current_job:
#             return {
#                 "job_id": self.current_job.id,
#                 "status": self.current_job.status,
#                 "start_time": self.current_job.start_time.isoformat() if self.current_job.start_time else None,
#                 "progress": len(self.extraction_results)
#             }
#         return {"status": "no_active_job"}


# # Convenience function for simple extraction
# def start_extraction(
#     states: List[str] = None,
#     y_axis: str = "Maker",
#     x_axis: str = "Month Wise",
#     apply_filter: bool = True,
#     state_delay_minutes: int = 5
# ) -> Dict:
#     """
#     Start extraction with simplified parameters
    
#     Args:
#         states: List of state codes (None = all states)
#         y_axis: Y-axis filter name
#         x_axis: X-axis filter name
#         apply_filter: Whether to apply vehicle category filters
#         state_delay_minutes: Minutes to wait between states
    
#     Returns:
#         Extraction summary dictionary
#     """
#     config = ExtractionConfig(
#         y_axis=y_axis,
#         x_axis=x_axis,
#         apply_vehicle_filter=apply_filter,
#         state_delay_minutes=state_delay_minutes
#     )
    
#     service = ExtractionService(config)
#     return service.start_full_extraction(states)

# if __name__ == "__main__":
#     # Example usage
#     summary = start_extraction(
#         states=None,  # All active states
#         y_axis="Maker",
#         x_axis="Month Wise",
#         apply_filter=True,
#         state_delay_minutes=2
#     )
    
#     print("\nExtraction Summary:")
#     for key, value in summary["overall_stats"].items():
#         print(f"{key}: {value}")