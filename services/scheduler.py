# services/scheduler.py
import schedule
import time
from db.session import SessionLocal
from db.models import JobTemplate
from services.extraction_service import start_extraction


def load_jobs():
    db = SessionLocal()
    jobs = db.query(JobTemplate).filter(JobTemplate.enabled == True).all()
    db.close()

    for job in jobs:
        print(f"⏳ Scheduling job {job.name} ({job.cron_expr})")
        # simple daily at HH:MM for now
        schedule.every().day.at(job.cron_expr).do(start_extraction)


def run_scheduler():
    load_jobs()
    while True:
        schedule.run_pending()
        time.sleep(60)

