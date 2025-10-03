# db/models.py
from sqlalchemy import (
    Column, String, Integer, BigInteger, Text, DateTime, JSON, ForeignKey,
    Boolean, TIMESTAMP, Float, Enum as SAEnum
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# ============================================================
# 1) Portal Site + Field + FieldOption
# ============================================================

class PortalSite(Base):
    __tablename__ = "portal_site"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    base_url = Column(String(300), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    robots_policy = Column(SAEnum("unknown", "allowed", "disallowed", name="robots_policy_enum"),
                           nullable=False, default="unknown")
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    fields = relationship("PortalField", back_populates="site")


class PortalField(Base):
    __tablename__ = "portal_field"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    site_id = Column(BigInteger, ForeignKey("portal_site.id"), nullable=False)
    field_name = Column(String(100), nullable=False)  # state, rto, year, x_axis, y_axis, etc.
    selector = Column(String(300))
    ui_type = Column(SAEnum("select", "input", "button", "checkbox", "other", name="ui_type_enum"),
                     nullable=False, default="select")
    depends_on_id = Column(BigInteger, ForeignKey("portal_field.id"))
    version_tag = Column(String(64))
    last_seen_at = Column(DateTime)
    created_at = Column(TIMESTAMP, server_default=func.now())

    site = relationship("PortalSite", back_populates="fields")
    options = relationship("PortalFieldOption", back_populates="field")


class PortalFieldOption(Base):
    __tablename__ = "portal_field_option"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    field_id = Column(BigInteger, ForeignKey("portal_field.id"), nullable=False)
    value_code = Column(String(128), nullable=False)
    label = Column(String(200), nullable=False)
    parent_code = Column(String(128))
    is_active = Column(Boolean, default=True, nullable=False)
    first_seen_at = Column(DateTime)
    last_seen_at = Column(DateTime)

    field = relationship("PortalField", back_populates="options")

# ============================================================
# 2) Scheduler
# ============================================================

class JobTemplate(Base):
    __tablename__ = "job_template"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    site_id = Column(BigInteger, ForeignKey("portal_site.id"), nullable=False)
    cron_expr = Column(String(64), nullable=False)
    timezone = Column(String(64), nullable=False, default="Asia/Kolkata")
    enabled = Column(Boolean, nullable=False, default=True)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# ============================================================
# 3) Workers / UA / Proxies
# ============================================================

# class WorkerNode(Base):
#     __tablename__ = "worker_node"

#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     name = Column(String(120), nullable=False, unique=True)
#     kind = Column(SAEnum("browser", "parser", "orchestrator", name="worker_kind_enum"),
#                   default="browser", nullable=False)
#     max_conc = Column(Integer, default=1, nullable=False)
#     status = Column(SAEnum("active", "draining", "offline", name="worker_status_enum"),
#                     default="active", nullable=False)
#     last_heartbeat = Column(DateTime)
#     created_at = Column(TIMESTAMP, server_default=func.now())


class UserAgentPool(Base):
    __tablename__ = "user_agent_pool"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class UserAgent(Base):
    __tablename__ = "user_agent"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pool_id = Column(BigInteger, ForeignKey("user_agent_pool.id"), nullable=False)
    ua_string = Column(String(500), nullable=False)
    is_mobile = Column(Boolean, nullable=False, default=False)
    weight = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())


# class ProxyPool(Base):
#     __tablename__ = "proxy_pool"

#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     name = Column(String(120), nullable=False, unique=True)
#     notes = Column(Text)
#     created_at = Column(TIMESTAMP, server_default=func.now())


# class ProxyEndpoint(Base):
#     __tablename__ = "proxy_endpoint"

#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     pool_id = Column(BigInteger, ForeignKey("proxy_pool.id"), nullable=False)
#     endpoint = Column(String(300), nullable=False)
#     region = Column(String(64))
#     weight = Column(Integer, default=1)
#     is_active = Column(Boolean, default=True, nullable=False)
#     last_used_at = Column(DateTime)

# ============================================================
# 4) States / RTO / Axis / Vehicle Filters
# ============================================================

class State(Base):
    __tablename__ = "states"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False, unique=True)
    total_rto = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class RTO(Base):
    __tablename__ = "rtos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    state_id = Column(BigInteger, ForeignKey("states.id"), nullable=False)
    name = Column(String(150), nullable=False)
    code = Column(String(32), nullable=False)
    value = Column(String(128))
    full_text = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class AxisFilter(Base):
    __tablename__ = "axis_filter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    axis = Column(SAEnum("X", "Y", name="axis_enum"), nullable=False)
    filter = Column(String(100), nullable=False)


class VehicleFilter(Base):
    __tablename__ = "vehicle_filter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, unique=True)
    code = Column(String(64))
    is_active = Column(Boolean, default=True, nullable=False)

# ============================================================
# 5) Files + Extraction + Logs (low-level extraction artifacts)
# ============================================================

class File(Base):
    __tablename__ = "files"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    url = Column(String(500))
    storage_key = Column(String(600))
    content_type = Column(String(100))
    file_size_bytes = Column(BigInteger)
    sha256 = Column(String(64))
    downloaded_at = Column(DateTime)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ExtractionRTO(Base):
    __tablename__ = "extraction_rto"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    state_id = Column(BigInteger, ForeignKey("states.id"), nullable=False)
    rto_id = Column(BigInteger, ForeignKey("rtos.id"))
    y_axis_id = Column(Integer, ForeignKey("axis_filter.id"), nullable=False)
    x_axis_id = Column(Integer, ForeignKey("axis_filter.id"), nullable=False)
    year_value = Column(Integer)
    vehicle_filter_id = Column(Integer, ForeignKey("vehicle_filter.id"))
    extraction_date = Column(DateTime, nullable=False)
    status = Column(SAEnum("queued", "running", "success", "error", "rate_limited",
                           name="extraction_rto_status_enum"),
                    default="queued")
    file_id = Column(BigInteger, ForeignKey("files.id"))
    extraction_data = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


# ============================================================
# 6) High-level Extraction Job & Result (used by services/extraction_service.py)
# ============================================================

class ExtractionJob(Base):
    """
    High-level orchestration job. Your services/extraction_service.py:
      - creates a job row at start
      - updates end_time/status/counters at finish
    """
    __tablename__ = "extraction_jobs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False, server_default=func.now())
    end_time = Column(DateTime, nullable=True)

    status = Column(SAEnum(
        "pending", "in_progress", "completed", "failed", "paused",
        name="extraction_job_status_enum"
    ), nullable=False, default="in_progress")

    # arbitrary config blob saved when job starts
    config = Column(JSON, nullable=True)

    # counters updated at the end
    total_files_downloaded = Column(Integer, nullable=False, default=0)
    total_errors = Column(Integer, nullable=False, default=0)

    # overall summary stats (e.g., states_processed, total_rtos, etc.)
    summary = Column(JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # optional: per-state/per-batch results
    results = relationship(
        "ExtractionResult",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class ExtractionResult(Base):
    """
    Optional per-state (or per-batch) rollup rows tied to an ExtractionJob.
    Not strictly required by your current code, but imported and useful.
    """
    __tablename__ = "extraction_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("extraction_jobs.id", ondelete="CASCADE"), nullable=False)

    # Useful rollup fields (aligns with summary fields in your service)
    state_id = Column(BigInteger, ForeignKey("states.id"), nullable=True)
    state_code = Column(String(10), nullable=True)
    state_name = Column(String(100), nullable=True)

    rtos_processed = Column(Integer, nullable=False, default=0)
    files_downloaded = Column(Integer, nullable=False, default=0)
    failures = Column(Integer, nullable=False, default=0)
    duration_minutes = Column(Float, nullable=True)
    errors = Column(JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    job = relationship("ExtractionJob", back_populates="results")
