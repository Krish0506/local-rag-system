from app.storage.postgres import engine
from app.storage.models import Base

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")