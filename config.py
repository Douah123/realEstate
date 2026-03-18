import os
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
LOCAL_MODEL_PATH = BASE_DIR / "model_pipeline_complet4.pkl"


def parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def normalize_origins(raw_value):
    if not raw_value:
        return []
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


def load_settings():
    database_url = os.getenv("DATABASE_URL")
    frontend_origins = normalize_origins(os.getenv("FRONTEND_ORIGINS"))
    enable_db_recording = parse_bool(
        os.getenv("ENABLE_DB_RECORDING"),
        default=bool(database_url),
    )

    return {
        "ENVIRONMENT": os.getenv("FLASK_ENV", "production"),
        "DEBUG": parse_bool(os.getenv("FLASK_DEBUG"), default=False),
        "JSON_SORT_KEYS": False,
        "MODEL_PATH": os.getenv("MODEL_PATH", str(LOCAL_MODEL_PATH)),
        "MODEL_S3_URI": os.getenv("MODEL_S3_URI"),
        "MODEL_CACHE_DIR": os.getenv(
            "MODEL_CACHE_DIR",
            str(Path(tempfile.gettempdir()) / "projet_cloud_api_models"),
        ),
        "SQLALCHEMY_DATABASE_URI": database_url,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "pool_pre_ping": True,
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "280")),
        },
        "ENABLE_DB_RECORDING": enable_db_recording,
        "AUTO_CREATE_DB": parse_bool(os.getenv("AUTO_CREATE_DB"), default=False),
        "FRONTEND_ORIGINS": frontend_origins,
        "FLASK_HOST": os.getenv("FLASK_HOST", "0.0.0.0"),
        "PORT": 8000,
    }
