"""
Excel Storage Service - Parse Excel files and store data in database
File: services/excel_storage_service.py
"""
import os
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from db.models import File, VehicleRegistrationData
from db.session import get_session

logger = logging.getLogger("app.services.excel_storage")


class ExcelStorageService:
    """Service to parse Excel files and store their data in the database"""

    def __init__(self):
        self.session: Optional[Session] = None

    def __enter__(self):
        self.session = next(get_session())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
            self.session.close()

    # ------------------------------------------------------------------
    # MAIN ENTRY POINT
    # ------------------------------------------------------------------
    def process_result_directory(self, result_dir: str = "result") -> Dict:
        """
        Process all Excel files from the latest extraction directory (e.g. result/vahan_extraction_human_YYYYMMDD_HHMMSS)
        """
        logger.info(f"Processing result directory: {result_dir}")

        if not os.path.exists(result_dir):
            logger.error(f"Result directory not found: {result_dir}")
            return {"error": "Directory not found"}

        # --------------------------------------------------------------
        # STEP 1: find the latest or today's extraction folder
        # --------------------------------------------------------------
        extraction_folders = [
            f for f in os.listdir(result_dir)
            if f.startswith("vahan_extraction_human_")
        ]
        if not extraction_folders:
            logger.warning("No extraction folders found in result directory")
            return {"error": "No extraction folders found"}

        # Prefer today's folder; fallback to latest
        today_prefix = f"vahan_extraction_human_{datetime.now().strftime('%Y%m%d')}"
        today_folders = [f for f in extraction_folders if f.startswith(today_prefix)]
        target_folder = sorted(today_folders or extraction_folders)[-1]
        extraction_path = os.path.join(result_dir, target_folder)

        logger.info(f"Processing only extraction folder: {extraction_path}")

        stats = {
            "total_files_found": 0,
            "files_processed": 0,
            "files_skipped": 0,
            "files_failed": 0,
            "total_records_created": 0,
            "errors": [],
        }

        # --------------------------------------------------------------
        # STEP 2: iterate through each state folder and Excel files
        # --------------------------------------------------------------
        for state_dir in os.listdir(extraction_path):
            state_path = os.path.join(extraction_path, state_dir)
            if not os.path.isdir(state_path):
                continue

            state_code = self._extract_state_code(state_dir)
            logger.info(f"Processing state directory: {state_dir} (code: {state_code})")

            for filename in os.listdir(state_path):
                if not filename.endswith(".xlsx"):
                    continue

                stats["total_files_found"] += 1
                file_path = os.path.join(state_path, filename)

                try:
                    # Create fresh service/session per file
                    with ExcelStorageService() as svc:
                        result = svc.process_excel_file(file_path, state_code)

                    if result["status"] == "success":
                        stats["files_processed"] += 1
                        stats["total_records_created"] += result["records_created"]
                    elif result["status"] == "skipped":
                        stats["files_skipped"] += 1
                    else:
                        stats["files_failed"] += 1
                        stats["errors"].append({
                            "file": filename,
                            "error": result.get("error", "Unknown error"),
                        })

                except Exception as e:
                    stats["files_failed"] += 1
                    error_msg = f"Error processing {filename}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    stats["errors"].append({"file": filename, "error": str(e)})

        logger.info(
            f"Processing complete: {stats['files_processed']} files processed, "
            f"{stats['total_records_created']} records created"
        )
        return stats

    # ------------------------------------------------------------------
    # PROCESS SINGLE FILE
    # ------------------------------------------------------------------
    def process_excel_file(self, file_path: str, state_code: Optional[str] = None) -> Dict:
        """Process a single Excel file and insert records"""
        try:
            filename = os.path.basename(file_path)
            metadata = self._extract_metadata_from_filename(filename)
            if state_code:
                metadata["state_code"] = state_code

            file_record = self._get_or_create_file_record(file_path)
            data_records = self._parse_excel_file(file_path, metadata)

            if not data_records:
                return {"status": "failed", "error": "No valid records found"}

            records_created = self._store_data_records(file_record.id, data_records, metadata)
            self.session.commit()
            self.session.expunge_all()

            return {
                "status": "success",
                "records_created": records_created,
                "file": filename,
            }

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            self.session.rollback()
            return {"status": "failed", "error": str(e)}

    # ------------------------------------------------------------------
    # DB HELPERS
    # ------------------------------------------------------------------
    def _get_or_create_file_record(self, file_path: str) -> File:
        """Get existing file record or create new one"""
        filename = os.path.basename(file_path)

        file_record = self.session.query(File).filter_by(storage_key=file_path).first()
        if file_record:
            return file_record

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else None
        file_record = File(
            file_name=filename,
            storage_key=file_path,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            file_size_bytes=file_size,
            downloaded_at=datetime.now(),
        )

        self.session.add(file_record)
        self.session.flush()
        logger.info(f"Created file record: {filename} (ID: {file_record.id})")
        return file_record

    def _store_data_records(self, file_id: int, data_records: List[Dict], metadata: Dict) -> int:
        """Store parsed data records in database"""
        records_created = 0

        for record in data_records:
            try:
                db_record = VehicleRegistrationData(
                    file_id=file_id,
                    maker_name=record["maker_name"],
                    s_no=record["s_no"],
                    jan=record["jan"],
                    feb=record["feb"],
                    mar=record["mar"],
                    apr=record["apr"],
                    may=record["may"],
                    jun=record["jun"],
                    jul=record["jul"],
                    aug=record["aug"],
                    sep=record["sep"],
                    oct=record["oct"],
                    nov=record["nov"],
                    dec=record["dec"],
                    total=record["total"],
                    year=metadata.get("year"),
                    state_code=metadata.get("state_code"),
                    rto_code=metadata.get("rto_code"),
                )
                self.session.add(db_record)
                records_created += 1
            except Exception as e:
                logger.error(f"Error storing record for maker {record.get('maker_name')}: {e}")

        self.session.flush()
        return records_created

    # ------------------------------------------------------------------
    # EXCEL PARSING
    # ------------------------------------------------------------------
    def _parse_excel_file(self, file_path: str, metadata: Dict) -> List[Dict]:
        """Parse Excel file and extract maker-wise monthly data"""
        try:
            # Load Excel (read all cells as strings)
            df = pd.read_excel(file_path, header=None, dtype=str)

            # 🔹 Drop completely empty columns (from merged cells or ghost columns)
            df = df.dropna(axis=1, how="all")

            # Detect year (from title line like "(2025)")
            year_match = re.search(r"\((\d{4})\)", " ".join(df.iloc[0:3].astype(str).values.flatten()))
            year = int(year_match.group(1)) if year_match else datetime.now().year
            metadata["year"] = year

            # Detect header row automatically
            header_row = self._find_header_row(df)
            if header_row is None:
                logger.warning(f"Could not find header row in {file_path}")
                return []

        # --------------------------
        # STEP 1: Assign and clean header
        # --------------------------
            df.columns = df.iloc[header_row].astype(str)
            df = df.iloc[header_row + 1:].reset_index(drop=True)

        # Clean header names: fill missing, remove 'nan'
            cols = (
                pd.Series(df.columns)
                .fillna("")
                .astype(str)
                .str.strip()
                .replace("nan", "", regex=False)
                .tolist()
            )

            # Forward-fill any blank headers caused by merged cells
            cols = pd.Series(cols).replace("", None).ffill().tolist()

        # 🔹 Ensure first two headers (S_NO & MAKER)
            if len(cols) >= 2:
                if cols[0] in [None, "", "NONE"]:
                    cols[0] = "S_NO"
                if cols[1] in [None, "", "NONE"]:
                    cols[1] = "MAKER"

            # 🔹 Drop duplicate last column if repeated
            if len(cols) > 2 and cols[-1] == cols[-2]:
                cols = cols[:-1]

            # Normalize headers
            cols = [str(c).strip().upper().replace(".", "").replace(" ", "_") for c in cols]

            # ✅ Make sure lengths match
            if len(cols) != df.shape[1]:
                logger.warning(
                    f"Header length mismatch fixed automatically for {os.path.basename(file_path)}: "
                    f"{len(cols)} cols vs {df.shape[1]} data cols"
                )

                if df.shape[1] - len(cols) == 1:
                    cols.append("TOTAL")
                elif len(cols) < df.shape[1]:
                    cols += [f"COL_{i}" for i in range(len(cols), df.shape[1])]
                else:
                    cols = cols[:df.shape[1]]
            df.columns = cols

        # --------------------------
        # STEP 2: Normalize names
        # --------------------------
            rename_map = {}
            for col in df.columns:
                c = re.sub(r"[-/]\d{2,4}", "", col)
                if any(m in c for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "TOTAL"]):
                    rename_map[col] = c
                elif "MAKER" in c:
                    rename_map[col] = "MAKER"
                elif "S" in c and "NO" in c:
                    rename_map[col] = "S_NO"

            df.rename(columns=rename_map, inplace=True)

        # --------------------------
        # STEP 3: Clean data rows
        # --------------------------
            df = df.dropna(how="all")
            df = df.map(lambda x: str(x).strip() if pd.notna(x) else "")

            logger.info(f"Detected columns for {os.path.basename(file_path)}: {df.columns.tolist()}")
            logger.info(f"First 3 rows:\n{df.head(3).to_string()}")

        # --------------------------
        # STEP 4: Convert to records
        # --------------------------
            data_records = []
            for _, row in df.iterrows():
                maker = row.get("MAKER", "").strip()
                if not maker or maker.upper() in ["MAKER", "SNO"]:
                    continue

                rec = {
                    "s_no": self._safe_int(row.get("S_NO")),
                    "maker_name": maker,
                    "jan": self._safe_int(row.get("JAN")),
                    "feb": self._safe_int(row.get("FEB")),
                    "mar": self._safe_int(row.get("MAR")),
                    "apr": self._safe_int(row.get("APR")),
                    "may": self._safe_int(row.get("MAY")),
                    "jun": self._safe_int(row.get("JUN")),
                    "jul": self._safe_int(row.get("JUL")),
                    "aug": self._safe_int(row.get("AUG")),
                    "sep": self._safe_int(row.get("SEP")),
                    "oct": self._safe_int(row.get("OCT")),
                    "nov": self._safe_int(row.get("NOV")),
                    "dec": self._safe_int(row.get("DEC")),
                    "total": self._safe_int(row.get("TOTAL")),
                }
                data_records.append(rec)

            logger.info(f"Parsed {len(data_records)} rows from {os.path.basename(file_path)} (year={year})")
            return data_records

        except Exception as e:
            logger.error(f"Error parsing Excel file {file_path}: {e}", exc_info=True)
            return []   

    # ------------------------------------------------------------------
    # UTILITIES
    # ------------------------------------------------------------------
    def _extract_metadata_from_filename(self, filename: str) -> Dict:
        metadata = {}
        parts = filename.replace(".xlsx", "").split("_")
        if parts:
            metadata["rto_code"] = parts[0]
        return metadata.copy()

    def _extract_state_code(self, state_dir: str) -> str:
        if "_" in state_dir:
            return state_dir.split("_")[0]
        return state_dir

    def _extract_year_from_dataframe(self, df: pd.DataFrame) -> Optional[int]:
        for idx in range(min(5, len(df))):
            row_str = str(df.iloc[idx].values)
            match = re.search(r"\[(\d{4})\]", row_str)
            if match:
                return int(match.group(1))
        return None

    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """
        Find the row index that contains headers like MAKER, JAN, FEB, TOTAL etc.
        Handles cases where first two columns (S No / Maker) may be NaN or merged.
        """
        keywords = ["MAKER", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "TOTAL"]
        for i in range(min(10, len(df))):
            row_text = " ".join(df.iloc[i].astype(str).str.upper())
        # require at least a few month keywords
            month_hits = sum(1 for k in keywords if k in row_text)
            if month_hits >= 4:  # heuristic: at least 4 month headers
                return i
        return None


    def _safe_int(self, value) -> Optional[int]:
        if pd.isna(value):
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    # ------------------------------------------------------------------
    # QUERY HELPERS
    # ------------------------------------------------------------------
    def get_file_data(self, file_id: int) -> List[VehicleRegistrationData]:
        return self.session.query(VehicleRegistrationData).filter_by(file_id=file_id).all()

    def get_maker_data(self, maker_name: str, state_code: str = None, year: int = None) -> List[VehicleRegistrationData]:
        query = self.session.query(VehicleRegistrationData).filter(
            VehicleRegistrationData.maker_name.ilike(f"%{maker_name}%")
        )
        if state_code:
            query = query.filter_by(state_code=state_code)
        if year:
            query = query.filter_by(year=year)
        return query.all()


# ----------------------------------------------------------------------
# Standalone convenience functions
# ----------------------------------------------------------------------
def process_all_excel_files(result_dir: str = "result") -> Dict:
    with ExcelStorageService() as service:
        return service.process_result_directory(result_dir)


def process_single_file(file_path: str, state_code: str = None) -> Dict:
    with ExcelStorageService() as service:
        return service.process_excel_file(file_path, state_code)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stats = process_all_excel_files()

    print("\n=== Processing Summary ===")
    print(f"Total files found: {stats['total_files_found']}")
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files skipped: {stats['files_skipped']}")
    print(f"Files failed: {stats['files_failed']}")
    print(f"Total records created: {stats['total_records_created']}")

    if stats["errors"]:
        print(f"\nErrors ({len(stats['errors'])}):")
        for error in stats["errors"][:5]:
            print(f"  - {error['file']}: {error['error']}")
