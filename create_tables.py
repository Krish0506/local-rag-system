from app.storage.postgres import engine
from app.storage.models import Base


def main():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()
