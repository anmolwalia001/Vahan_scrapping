# Database Integration Guide

This guide explains how to integrate the database storage system with your Vahan extraction service.

## Overview

The integration adds:
- **Database tracking** of all extractions (jobs, results, files, RTOs)
- **File management** with SHA256 hashing and metadata
- **Skip existing** functionality to avoid re-extracting recent data
- **Job statistics** and progress tracking
- **Error tracking** for debugging

## Files Created

1. **`services/db_extraction_service.py`** - Database service layer
2. **Updated `services/extraction_service_human_like.py`** - Extraction service with DB integration
3. **Helper methods** for existing extractors

## Setup Steps

### Step 1: Add Helper Methods to Extractors

#### In `extractor/extract_axis.py`:

```python
from typing import Optional
import logging

logger = logging.getLogger("app.extractor.axis")

class AxisExtractor:
    # ... existing code ...
    
    def get_axis_id_by_label(self, label: str) -> Optional[int]:
        """Get axis ID by label text"""
        from db.session import get_db
        from db.models import AxisFilter
        
        session = next(get_db())
        try:
            axis = session.query(AxisFilter).filter(
                AxisFilter.axis_name == label
            ).first()
            
            return axis.id if axis else None
        except Exception as e:
            logger.error(f"Error getting axis ID: {e}")
            return None
        finally:
            session.close()
```

#### In `extractor/extract_vehicle_filter.py`:

```python
from typing import Optional
import logging

logger = logging.getLogger("app.extractor.vehicle_filter")

class VehicleFilterExtractor:
    # ... existing code ...
    
    def get_filter_id_by_name(self, filter_name: str) -> Optional[int]:
        """Get vehicle filter ID by name"""
        from db.session import get_db
        from db.models import VehicleFilter
        
        session = next(get_db())
        try:
            vehicle_filter = session.query(VehicleFilter).filter(
                VehicleFilter.filter_name == filter_name
            ).first()
            
            return vehicle_filter.id if vehicle_filter else None
        except Exception as e:
            logger.error(f"Error getting vehicle filter ID: {e}")
            return None
        finally:
            session.close()
```

### Step 2: Update Database Models (if needed)

Ensure your `ExtractionJob` model has the relationship defined:

```python
# In db/models.py - ExtractionJob class
class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"
    # ... existing fields ...
    
    # Add this relationship if not present
    results = relationship("ExtractionResult", back_populates="job", cascade="all, delete-orphan")
```

### Step 3: Install the New Service Files

1. Copy `db_extraction_service.py` to `services/` directory
2. Replace `extraction_service_human_like.py` with the new version

### Step 4: Test the Integration

Create a test script:

```python
# test_db_integration.py
from services.extraction_service_human_like import start_human_like_extraction

# Test with one state and database enabled
summary = start_human_like_extraction(
    states=['DL'],  # Delhi only for testing
    enable_db=True,
    skip_existing=True
)

print(f"\nExtraction Summary:")
print(f"Job ID: {summary.get('job_id')}")
print(f"Duration: {summary['duration_minutes']:.1f} minutes")
print(f"Files Downloaded: {summary['files_downloaded']}")
print(f"Success Rate: {summary['success_rate']}%")

# Check database for the job
if summary.get('job_id'):
    from services.db_extraction_service import DBExtractionService
    db_service = DBExtractionService()
    stats = db_service.get_job_statistics(summary['job_id'])
    print(f"\nDatabase Statistics:")
    print(stats)
```

## Usage Examples

### Basic Usage (with database)

```python
from services.extraction_service_human_like import start_human_like_extraction

# Extract all states with database tracking
summary = start_human_like_extraction(
    states=None,  # All states
    enable_db=True,
    skip_existing=True
)
```

### Extract Specific States

```python
# Extract just Delhi and Maharashtra
summary = start_human_like_extraction(
    states=['DL', 'MH'],
    enable_db=True,
    skip_existing=False  # Re-extract even if exists
)
```

### Without Database (legacy mode)

```python
# If you want to run without database tracking
summary = start_human_like_extraction(
    states=['DL'],
    enable_db=False,
    skip_existing=False
)
```

### Advanced Configuration

```python
from services.extraction_service_human_like import (
    HumanLikeExtractionService,
    ExtractionConfig,
    HumanLikeDelayConfig
)

# Custom delay configuration
delay_config = HumanLikeDelayConfig(
    between_states=(30, 60),  # 30-60 seconds between states
    max_retries=3,
    detection_cooldown=(180, 360)  # 3-6 minutes cooldown
)

# Custom extraction configuration
config = ExtractionConfig(
    y_axis="Maker",
    x_axis="Month Wise",
    apply_vehicle_filter=True,
    vehicle_filter_categories=[
        ["MOTOR CAR", "MOTOR CAB"],
        ["ELECTRIC(BOV)", "PURE EV"]
    ],
    enable_db_storage=True,
    skip_existing=True,
    delay_config=delay_config
)

# Create service and run
service = HumanLikeExtractionService(config)
summary = service.start_extraction(['DL', 'MH'])
```

## Database Schema

### Files Stored in Database

#### `extraction_jobs` table
- Tracks overall extraction jobs
- Status: queued, running, completed, failed
- Records start/end times

#### `extraction_results` table
- Per-state summary results
- Linked to extraction job
- Tracks RTOs processed, files downloaded, failures

#### `extraction_rto` table
- Individual RTO extraction records
- Links to state, RTO, axis filters, vehicle filters
- Stores extraction date and status
- Links to downloaded file

#### `files` table
- File metadata and storage information
- SHA256 hash for deduplication
- File size, content type
- Storage key (local path or cloud URL)

## Key Features

### 1. Skip Existing Extractions

The system checks if an RTO was already extracted recently (default: 7 days):

```python
# In your extraction config
config = ExtractionConfig(
    skip_existing=True  # Skip RTOs extracted in last 7 days
)
```

### 2. File Deduplication

Files are deduplicated using SHA256 hashing. If the same file is downloaded multiple times, only one record is created.

### 3. Job Statistics

Query job statistics anytime:

```python
from services.db_extraction_service import DBExtractionService

db_service = DBExtractionService()
stats = db_service.get_job_statistics(job_id=123)

print(stats)
# Output:
# {
#     'job_id': 123,
#     'status': 'completed',
#     'started_at': '2025-09-30T10:00:00',
#     'completed_at': '2025-09-30T12:30:00',
#     'states_processed': 5,
#     'total_rtos': 150,
#     'total_files': 145,
#     'total_failures': 5,
#     'success_rate': 96.67
# }
```

### 4. Error Tracking

All errors are stored in the database for analysis:

```python
# Errors stored in extraction_results.errors (JSON array)
# Can query failed extractions
from db.models import ExtractionResult
from db.session import get_db

session = next(get_db())
failed_results = session.query(ExtractionResult).filter(
    ExtractionResult.failures > 0
).all()

for result in failed_results:
    print(f"State: {result.state_name}")
    print(f"Errors: {result.errors}")
```

## File Storage Notes

### Current Implementation (Local Storage)

Files are currently stored locally in the `result/` directory. The `files.storage_key` column stores the local file path.

The `files.url` column is NULL for now but reserved for future cloud storage integration.

### Future Cloud Storage

To integrate cloud storage (S3, GCS, etc.):

1. After downloading a file, upload it to cloud storage
2. Update the `files.url` column with the cloud URL
3. Optionally delete the local file to save space

Example integration point:

```python
# In _process_rto_with_human_behavior method, after download:
if self._download_with_retry(state_dir, filename):
    file_path = os.path.join(state_dir, filename)
    
    # Upload to cloud (your implementation)
    cloud_url = upload_to_cloud(file_path)
    
    # Create file record with cloud URL
    file_id = self.db_service.create_file_record(
        file_path=file_path,
        storage_key=cloud_url  # or keep local path
    )
    
    # Update URL separately if needed
    # update_file_url(file_id, cloud_url)
```

## Monitoring and Maintenance

### Query Recent Jobs

```python
from db.models import ExtractionJob
from db.session import get_db
from datetime import datetime, timedelta

session = next(get_db())

# Get jobs from last 24 hours
cutoff = datetime.now() - timedelta(hours=24)
recent_jobs = session.query(ExtractionJob).filter(
    ExtractionJob.started_at >= cutoff
).order_by(ExtractionJob.started_at.desc()).all()

for job in recent_jobs:
    print(f"Job {job.id}: {job.status} - {job.started_at}")
```

### Find Duplicate Files

```python
from db.models import File
from sqlalchemy import func

# Find files with same SHA256 (duplicates)
duplicates = session.query(
    File.sha256,
    func.count(File.id).label('count')
).group_by(File.sha256).having(func.count(File.id) > 1).all()

for sha256, count in duplicates:
    print(f"Hash {sha256}: {count} copies")
```

## Troubleshooting

### Issue: "Axis not found in database"

**Solution**: Ensure axis filters are seeded in database:

```python
from extractor.extract_axis import AxisExtractor

extractor = AxisExtractor()
# This should populate the axis_filter table
```

### Issue: "Vehicle filter not found"

**Solution**: Ensure vehicle filters are seeded:

```python
from extractor.extract_vehicle_filter import VehicleFilterExtractor

extractor = VehicleFilterExtractor()
# This should populate the vehicle_filter table
```

### Issue: File records not created

**Solution**: Check file paths are correct and files exist before calling `create_file_record()`.

### Issue: Skip existing not working

**Solution**: Verify that:
1. `y_axis_id` and `x_axis_id` are being set correctly
2. Previous extractions have `status='success'`
3. Check the `days_old` parameter (default 7 days)

## Performance Considerations

- Database operations add ~100-200ms per RTO
- File hashing adds ~50-100ms per file
- Use `skip_existing=True` to avoid redundant work
- Consider batch operations for large extractions

## Best Practices

1. **Always enable database storage** for production runs
2. **Use skip_existing=True** to avoid re-extracting data
3. **Monitor job_id** to track extraction progress
4. **Check error logs** regularly for patterns
5. **Back up the database** before major changes
6. **Clean up old extraction records** periodically

## Migration from Old System

If you have existing extraction code without database:

1. Keep both systems running in parallel
2. Test new system with small state subset
3. Verify data integrity
4. Gradually migrate to new system
5. Archive old results as needed

## Summary

The database integration provides:
- Complete audit trail of all extractions
- Automatic deduplication
- Error tracking and analysis
- Progress monitoring
- Skip already-extracted data
- Foundation for cloud storage integration

All while maintaining the human-like behavior and retry mechanisms of the original system.