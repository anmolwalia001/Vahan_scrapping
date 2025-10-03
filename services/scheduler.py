# services/scheduler.py
import time
from db.session import SessionLocal
from db.models import JobTemplate
from services.run_human_like_extraction import main as run_human_extraction
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler(timezone="Asia/Kolkata")

def run_scheduler():
    db = SessionLocal()
    jobs = db.query(JobTemplate).filter(JobTemplate.enabled == True).all()
    db.close()

    for job in jobs:
        print(f"⏳ Scheduling job {job.name} ({job.cron_expr})")
        scheduler.add_job(

            run_human_extraction,
            trigger="cron",
            **dict(zip(["minute", "hour", "day", "month", "day_of_week"], job.cron_expr.split()))
        )

    print("✅ Scheduler started. Waiting for jobs...")
    scheduler.start()

if __name__ == "__main__":
    run_scheduler()
