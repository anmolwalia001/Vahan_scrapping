# init_db.py
from db.session import engine
from db.models import Base

print("🚀 Creating all tables in database...")
Base.metadata.create_all(bind=engine)
print("✅ Done. Tables are ready!")
