"""Settings."""
import os

AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


def load_settings():
    return {
        "database_url": os.environ.get("DATABASE_URL", "sqlite:///shop.db"),
        "debug": os.environ.get("DEBUG", "false") == "true",
    }
