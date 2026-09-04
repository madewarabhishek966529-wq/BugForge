from backend.app.database.database import engine, Base
from backend.app.models import project, bug, analysis_result  # noqa

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")
