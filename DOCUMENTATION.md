# Feat_Vahan

 Feat_Vahan is a modular, extensible Python project for large-scale scraping and data extraction from the Vahan Portal (and potentially other government transport portals).

## The project is designed to handle:

Web scraping with anti-bot measures (stealth Chrome, human-like delays, proxy support).

Data orchestration (axis/state/RTO/vehicle filter combinations).

Database persistence (SQLAlchemy ORM + MySQL).

Result storage & export (Excel/CSV).

Job scheduling (cron-like via APScheduler).

Resumable & fault-tolerant workflows (error handling, retries, job status tracking).

## ⚙️ Project Structure
```
Feat_Vahan/
├── .env                      # Environment variables (DB, proxy, etc.)
├── requirements.txt          # Python dependencies
├── configs/                  # Centralized configuration
│   ├── logging.yaml          # Logging handlers, formatters, and levels
│   └── setting.py            # Environment loader (DB creds, proxy, timeouts)
├── db/                       # Database layer
│   ├── models.py             # SQLAlchemy ORM models
│   ├── session.py            # Session management (engine, SessionLocal)
│   └── seed.py               # Seeder for states, RTOS, job templates
├── extractor/                # Portal-specific extractors
│   ├── extract_states.py     # Get list of states
│   ├── extract_all_rto.py    # Extract RTOs for a given state
│   ├── extract_axis.py       # Handle X/Y axis setup
│   ├── extract_vehicle_filter.py # Apply vehicle category filters
│   └── __init__.py
├── scrapper/                 # Browser automation
│   ├── browser.py            # VahanBrowser wrapper (stealth, proxy, retries)
│   ├── element_cache.py      # Element caching for speed
│   ├── element_discovery.py  # Debugging & discovery utilities
├── services/                 # Business logic / orchestration
│   ├── extraction_service_human_like.py # Core extraction with delays & retries
│   ├── db_extraction_service.py  # DB write helpers (jobs, results, files)
│   ├── run_human_like_extraction.py # CLI entrypoint for running jobs
│   ├── scheduler.py          # APScheduler job loader (daily/cron jobs)
│   ├── file_handler.py       # File move, rename, cleanup
│   ├── proxy_manager.py      # Proxy rotation and validation
│   ├── check_proxy.py        # Proxy health check
├── storage/                  # Output handlers
│   ├── excel_export.py       # Export results to Excel
│   └── __init__.py
├── utils/                    # Utility helpers
│   ├── constants.py          # Global constants
│   └── helpers.py            # String sanitizers, retry wrappers, etc.
├── logs/                     # Runtime logs
├── result/                   # Extraction output (Excel files)
├── tests/                    # Unit/integration tests
│   ├── test_db.py
│   ├── test_pipeline.py
│   └── test_scrapper.py
```

## 🗄️ Database Schema

Core tables (simplified):

- portal_sites → external sites (Vahan, others in future).

- states → State list (name, code).

- rtos → RTOs under each state.

- portal_fields / portal_field_options → X/Y axis values and filters.

- extraction_jobs → top-level job run (status, config, counters, summary).

- extraction_results → per-state results (RTOS processed, successes, failures).

- files → downloaded Excel metadata (path, size, hash).

- extraction_rto_records → per-RTO + filter execution log.

This separation ensures traceability: every file can be linked back to its job → state → RTO → filter.

# 🧩 Core Components
## 🖥️ Scrapper Layer (scrapper/)

Wraps Selenium with stealth capabilities.

Handles browser initialization, proxies, and error recovery.

Provides element caching for repetitive DOM operations.

## 📊 Extractor Layer (extractor/)

Encapsulates logic for axis selection, state dropdowns, RTO listings, and vehicle filters.

Independent modules → easy to test and replace if DOM changes.

## ⚙️ Services Layer (services/)

- Human-like Extraction Service:

- Sequentially loops states → RTOs → filters.

- Adds randomized human-like delays (after_filter_apply, between_states).

- Detects bot-blocks (e.g., ERR_NETWORK_CHANGED) and recovers via browser reset.

> DBExtractionService:

- Creates & updates job records (pending → in_progress → completed/failed).

- Saves per-state results and per-RTO extraction logs.

- Tracks file downloads (files table).

> Scheduler:

- APScheduler-based cron runner.

- Pulls job templates from DB and registers jobs.

- Supports per-site, per-filter job templates.

## 📦 Storage Layer (storage/)

Exports results into Excel (excel_export.py).

Could be extended for CSV, JSON, cloud upload (GCS/S3).

# 🔄 Workflow

Job Creation

**Seeder (db/seed.py)** inserts templates into job_templates.

**Scheduler (services/scheduler.py)** picks enabled jobs.

**Job Start**

Creates extraction_jobs row (status = in_progress).

Loads Y/X axis and vehicle filters from DB.

State & RTO Processing

Selects state dropdown → iterates all RTOs.

Applies filters sequentially.

Downloads Excel files (stored in /result + DB entry).

DB Logging

Each file = files row.

Each filter execution = extraction_rto_records.

Each state summary = extraction_results.

Job End

Updates extraction_jobs.end_time, status, and counters.

## ▶️ Usage
Run Once (All States)
python -m services.run_human_like_extraction

Schedule via DB JobTemplate
python -m services.scheduler

Keeps running; executes jobs as per cron_expr.

Debug Scraper
python -m scrapper.element_discovery

## 🔐 Environment Variables (.env)
DB_USER=root
DB_PASSWORD=****
DB_HOST=localhost
DB_PORT=3306
DB_NAME=vahan_db

PROXY_ENABLED=false
PROXY_URL=http://user:pass@proxy:port
LOG_LEVEL=INFO

## 🧪 Testing

Run all tests:

pytest tests/

### Run DB-specific:

pytest tests/test_db.py

# 🚀 Roadmap / Extensions

✅ Multi-axis support (Maker vs Month Wise, Fuel Type vs Year).

✅ Multi-filter extraction (MOTOR CAR, EV).

🔲 Distributed scraping across workers.

🔲 Export to BigQuery / cloud storage.

🔲 Web dashboard for monitoring jobs.

🔲 Captcha solver integration.