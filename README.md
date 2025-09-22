# Feat_Vahan

Feat_Vahan is a modular Python project for extracting, scraping, and managing vehicle-related data from various sources. It is organized for scalability and maintainability, with clear separation of concerns across its modules.

## Project Structure

```
Feat_Vahan/
├── .env
├── .gitignore
├── main.py
├── requirements.txt
├── configs/
│   ├── logging.yaml
│   └── setting.py
├── db/
│   ├── models.py
│   ├── session.py
│   └── seed.py
├── extractor/
│   ├── extract_all_rto.py
│   ├── extract_axis.py
│   ├── extract_states.py
│   ├── extract_vehicle_filter.py
│   └── __init__.py
├── logs/
├── result/
├── scrapper/
│   ├── browser.py
│   ├── element_cache.py
│   ├── element_discovery.py
│   └── __init__.py
├── services/
│   ├── file_handler.py
│   ├── proxy_manager.py
│   └── scheduler.py
├── storage/
│   ├── excel_export.py
│   └── __init__.py
├── tests/
│   ├── test_db.py
│   ├── test_pipeline.py
│   └── test_scrapper.py
├── utils/
│   ├── constants.py
│   └── helpers.py
├── myenv/
```

## Setup

1. Clone the repository:
   ```
   git clone <repo-url>
   cd Feat_Vahan
   ```
2. Create and activate a Python virtual environment:
   ```
   python -m venv myenv
   myenv\Scripts\activate  # On Windows
   source myenv/bin/activate  # On Linux/Mac
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`.
5. Adjust settings in `configs/setting.py` and `configs/logging.yaml` as needed.

## Usage

- Run the main application:
  ```
  python main.py
  ```
- Run individual modules (example):
  ```
  python -m extractor.extract_all_rto
  python -m scrapper.element_discovery
  ```
- Run tests:
  ```
  python -m unittest discover tests
  ```
