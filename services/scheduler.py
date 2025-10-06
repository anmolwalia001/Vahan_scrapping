# services/scheduler.py
import logging
from db.session import SessionLocal
from db.models import JobTemplate
from services.run_human_like_extraction import main as run_human_extraction
from scrapper.element_discovery import ElementDiscoverer
from apscheduler.schedulers.blocking import BlockingScheduler

logger = logging.getLogger("app.scheduler")
scheduler = BlockingScheduler(timezone="Asia/Kolkata")


def run_extraction_with_discovery():
    """
    Wrapper function that runs element discovery before extraction
    """
    try:
        logger.info("=== Starting Element Discovery ===")
        discoverer = ElementDiscoverer()
        
        # Auto-discover missing/stale selectors
        missing_results = discoverer.auto_discover_missing()
        
        if missing_results:
            logger.info(f"Discovered {len(missing_results)} elements")
            
            # Check if critical elements were found
            critical_failures = [
                field for field, success in missing_results.items() 
                if not success and field in ['state', 'rto', 'main_refresh', 'excel_export']
            ]
            
            if critical_failures:
                logger.error(f"Critical elements missing: {critical_failures}")
                logger.error("Aborting extraction - fix element discovery first")
                return
        
        logger.info("=== Element Discovery Complete ===")
        logger.info("=== Starting Extraction ===")
        
        # Run the actual extraction
        run_human_extraction()
        
        logger.info("=== Extraction Complete ===")
        
    except Exception as e:
        logger.error(f"Error in extraction pipeline: {e}", exc_info=True)


def load_and_schedule_jobs():
    """Load jobs from database and schedule them"""
    db = SessionLocal()
    try:
        jobs = db.query(JobTemplate).filter(JobTemplate.enabled == True).all()
        
        if not jobs:
            logger.warning("No enabled jobs found in database")
            logger.info("Adding a default job to run immediately for testing...")
            
            # Run once immediately for testing
            scheduler.add_job(
                run_extraction_with_discovery,
                trigger='date',  # Run once immediately
                id='immediate_test_job'
            )
            logger.info("Scheduled immediate test run")
        
        for job in jobs:
            logger.info(f"Scheduling job: {job.name} ({job.cron_expr})")
            
            # Parse cron expression (assuming format: "HH:MM" for daily jobs)
            if ':' in job.cron_expr:
                # Daily job at specific time
                hour, minute = job.cron_expr.split(':')
                scheduler.add_job(
                    run_extraction_with_discovery,
                    trigger='cron',
                    hour=int(hour),
                    minute=int(minute),
                    id=f'job_{job.id}',
                    name=job.name
                )
                logger.info(f"  -> Scheduled daily at {job.cron_expr}")
            else:
                # Full cron expression
                cron_parts = job.cron_expr.split()
                if len(cron_parts) == 5:
                    minute, hour, day, month, day_of_week = cron_parts
                    scheduler.add_job(
                        run_extraction_with_discovery,
                        trigger='cron',
                        minute=minute,
                        hour=hour,
                        day=day,
                        month=month,
                        day_of_week=day_of_week,
                        id=f'job_{job.id}',
                        name=job.name
                    )
                    logger.info(f"  -> Scheduled with cron: {job.cron_expr}")
                else:
                    logger.error(f"Invalid cron expression for job {job.name}: {job.cron_expr}")
    
    finally:
        db.close()


def run_scheduler():
    """Main scheduler entry point"""
    logger.info("Starting APScheduler...")

    # Load jobs from database
    load_and_schedule_jobs()

    # Print scheduled jobs
    jobs = scheduler.get_jobs()
    if jobs:
        logger.info(f"Total scheduled jobs: {len(jobs)}")
        for job in jobs:
            # v4.x Job object doesn't have .next_run_time
            next_run = scheduler.get_next_run_time(job.id) if hasattr(scheduler, "get_next_run_time") else None
            logger.info(f"  - {job.name} (next run: {next_run})")
    else:
        logger.warning("No jobs scheduled!")

    logger.info("Scheduler active. Press Ctrl+C to exit.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")



if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    run_scheduler()