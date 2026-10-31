# This file holds project configuration.

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_FOLDER / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "aab_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "aab_e_panah")
