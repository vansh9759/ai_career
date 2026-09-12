import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "AIResumeAnalyzerSecretKey")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Detect Vercel Serverless environment
    is_vercel = os.environ.get("VERCEL") == "1" or "AWS_LAMBDA_FUNCTION_NAME" in os.environ

    if is_vercel:
        db_path = "/tmp/database.db"
        upload_path = "/tmp/uploads"
    else:
        db_path = os.path.join(BASE_DIR, "database.db")
        upload_path = os.path.join(BASE_DIR, "uploads")

    try:
        os.makedirs(upload_path, exist_ok=True)
    except Exception:
        pass

    # PostgreSQL Managed DB Support (Render, Supabase, Neon) or SQLite Fallback
    raw_db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if raw_db_url:
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = upload_path

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024