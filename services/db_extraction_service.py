# services/db_extraction_service.py
"""
Database service for tracking extractions with proper file and status management
"""

import logging
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.models import ExtractionRTO, File, ExtractionJob, ExtractionResult
from db.session import get_session

logger = logging.getLogger("app.services.db_extraction")


class DBExtractionService:
    """Service for managing extraction records in database"""
    
    def __init__(self, db: Session = None):
        """
        Initialize DB extraction service
        
        Args:
            db: Optional SQLAlchemy session. If None, will create new sessions per operation.
        """
        self.db = db
        self._owns_session = db is None
    
    def _get_session(self) -> Session:
        """Get database session"""
        if self.db:
            return self.db
        return next(get_session())
    
    def _close_session(self, session: Session):
        """Close session if we own it"""
        if self._owns_session and session:
            session.close()
    
    def create_extraction_job(self, 
                             state_codes: List[str],
                             y_axis_id: int,
                             x_axis_id: int,
                             vehicle_filter_ids: List[int] = None,
                             year_value: int = None) -> Optional[int]:
        """
        Create a new extraction job record
        
        Args:
            state_codes: List of state codes to extract
            y_axis_id: Y-axis filter ID
            x_axis_id: X-axis filter ID
            vehicle_filter_ids: Optional list of vehicle filter IDs
            year_value: Optional year value
            
        Returns:
            Job ID if successful, None otherwise
        """
        session = self._get_session()
        try:
            job = ExtractionJob(
                state_codes=state_codes,
                y_axis_id=y_axis_id,
                x_axis_id=x_axis_id,
                vehicle_filter_ids=vehicle_filter_ids or [],
                year_value=year_value,
                status="queued",
                started_at=datetime.now()
            )
            
            session.add(job)
            session.commit()
            
            job_id = job.id
            logger.info(f"Created extraction job: {job_id}")
            return job_id
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating extraction job: {e}")
            session.rollback()
            return None
        finally:
            self._close_session(session)
    
    def update_job_status(self, job_id: int, status: str, error_message: str = None):
        """
        Update extraction job status
        
        Args:
            job_id: Job ID
            status: New status (running, completed, failed, cancelled)
            error_message: Optional error message if failed
        """
        session = self._get_session()
        try:
            job = session.query(ExtractionJob).filter_by(id=job_id).first()
            if job:
                job.status = status
                if status == "completed":
                    job.end_time = datetime.now()
                if error_message:
                    job.config = {**(job.config or {}), "error_message": error_message}
                session.commit()
            else:
                logger.warning(f"Job {job_id} not found")
        except SQLAlchemyError as e:
            logger.error(f"Error updating job status: {e}")
            session.rollback()
        finally:
            self._close_session(session)
    
    def create_file_record(self, 
                          file_path: str,
                          storage_key: str = None) -> Optional[int]:
        """
        Create a file record in database
        
        Args:
            file_path: Path to the downloaded file
            storage_key: Optional cloud storage key (for future use)
            
        Returns:
            File ID if successful, None otherwise
        """
        session = self._get_session()
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Calculate file hash
            sha256_hash = self._calculate_file_hash(file_path)
            
            # Check if file already exists (by hash)
            existing_file = session.query(File).filter_by(sha256=sha256_hash).first()
            if existing_file:
                logger.info(f"File already exists in DB: {existing_file.id}")
                return existing_file.id
            
            # Get file stats
            file_size = file_path_obj.stat().st_size
            file_name = file_path_obj.name
            
            # Determine content type
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if file_path.endswith('.xls'):
                content_type = "application/vnd.ms-excel"
            
            # Create file record
            file_record = File(
                file_name=file_name,
                url=None,  # Will be populated when uploaded to cloud
                storage_key=storage_key or file_path,  # Use local path as storage key for now
                content_type=content_type,
                file_size_bytes=file_size,
                sha256=sha256_hash,
                downloaded_at=datetime.now()
            )
            
            session.add(file_record)
            session.commit()
            
            file_id = file_record.id
            logger.info(f"Created file record: {file_id} for {file_name}")
            return file_id
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating file record: {e}")
            session.rollback()
            return None
        finally:
            self._close_session(session)
    
    def create_extraction_rto_record(self,
                                    state_id: int,
                                    rto_id: int,
                                    y_axis_id: int,
                                    x_axis_id: int,
                                    vehicle_filter_id: int = None,
                                    year_value: int = None,
                                    file_id: int = None,
                                    status: str = "success",
                                    extraction_data: Dict = None) -> Optional[int]:
        """
        Create an extraction RTO record
        
        Args:
            state_id: State ID
            rto_id: RTO ID
            y_axis_id: Y-axis filter ID
            x_axis_id: X-axis filter ID
            vehicle_filter_id: Optional vehicle filter ID
            year_value: Optional year value
            file_id: Optional file ID if downloaded
            status: Extraction status (success, error, rate_limited)
            extraction_data: Optional metadata about extraction
            
        Returns:
            Extraction RTO ID if successful, None otherwise
        """
        session = self._get_session()
        try:
            extraction_rto = ExtractionRTO(
                state_id=state_id,
                rto_id=rto_id,
                y_axis_id=y_axis_id,
                x_axis_id=x_axis_id,
                vehicle_filter_id=vehicle_filter_id,
                year_value=year_value,
                extraction_date=datetime.now(),
                status=status,
                file_id=file_id,
                extraction_data=extraction_data or {}
            )
            
            session.add(extraction_rto)
            session.commit()
            
            extraction_id = extraction_rto.id
            logger.info(f"Created extraction RTO record: {extraction_id}")
            return extraction_id
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating extraction RTO record: {e}")
            session.rollback()
            return None
        finally:
            self._close_session(session)
    
    def create_extraction_result(self,
                             job_id: int,
                             state_id: int,
                             state_code: str,
                             state_name: str,
                             rtos_processed: int,
                             files_downloaded: int,
                             failures: int,
                             duration_minutes: float,
                             errors: List[str] = None) -> Optional[int]:
        """
         Create an extraction result summary for a state
        """
        session = self._get_session()
        try:
            result = ExtractionResult(
            job_id=job_id,
            state_id=state_id,
            state_code=state_code,
            state_name=state_name,
            rtos_processed=rtos_processed,
            files_downloaded=files_downloaded,
            failures=failures,
            duration_minutes=duration_minutes,
            errors=errors or []
            )
        
            session.add(result)
            session.commit()
        
            result_id = result.id
            logger.info(f"Created extraction result: {result_id} for state {state_name}")
            return result_id

        except SQLAlchemyError as e:
            logger.error(f"Error creating extraction result: {e}")
            session.rollback()
            return None
        finally:
            self._close_session(session)

    
    def check_extraction_exists(self,
                               rto_id: int,
                               y_axis_id: int,
                               x_axis_id: int,
                               vehicle_filter_id: int = None,
                               year_value: int = None,
                               days_old: int = 7) -> bool:
        """
        Check if extraction already exists for given parameters
        
        Args:
            rto_id: RTO ID
            y_axis_id: Y-axis filter ID
            x_axis_id: X-axis filter ID
            vehicle_filter_id: Optional vehicle filter ID
            year_value: Optional year value
            days_old: Only consider extractions newer than this many days
            
        Returns:
            True if recent extraction exists, False otherwise
        """
        session = self._get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            query = session.query(ExtractionRTO).filter(
                ExtractionRTO.rto_id == rto_id,
                ExtractionRTO.y_axis_id == y_axis_id,
                ExtractionRTO.x_axis_id == x_axis_id,
                ExtractionRTO.status == "success",
                ExtractionRTO.extraction_date >= cutoff_date
            )
            
            if vehicle_filter_id:
                query = query.filter(ExtractionRTO.vehicle_filter_id == vehicle_filter_id)
            
            if year_value:
                query = query.filter(ExtractionRTO.year_value == year_value)
            
            exists = query.first() is not None
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking extraction existence: {e}")
            return False
        finally:
            self._close_session(session)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def get_job_statistics(self, job_id: int) -> Optional[Dict]:
        """
        Get statistics for a job
        
        Args:
            job_id: Job ID
            
        Returns:
            Dictionary with job statistics or None
        """
        session = self._get_session()
        try:
            job = session.query(ExtractionJob).filter_by(id=job_id).first()
            if not job:
                return None
            
            results = session.query(ExtractionResult).filter_by(job_id=job_id).all()
            
            total_rtos = sum(r.rtos_processed for r in results)
            total_files = sum(r.files_downloaded for r in results)
            total_failures = sum(r.failures for r in results)
            
            return {
                'job_id': job_id,
                'status': job.status,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'states_processed': len(results),
                'total_rtos': total_rtos,
                'total_files': total_files,
                'total_failures': total_failures,
                'success_rate': round((total_files / total_rtos * 100) if total_rtos > 0 else 0, 2)
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting job statistics: {e}")
            return None
        finally:
            self._close_session(session)


# Convenience function for use in extraction service
def create_db_service() -> DBExtractionService:
    """Create a new DB extraction service instance"""
    return DBExtractionService()