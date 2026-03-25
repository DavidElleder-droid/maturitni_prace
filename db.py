import logging
import os

import pyodbc
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Zapnutí ODBC connection poolingu.
# Musí být nastaveno před vytvářením connection.
pyodbc.pooling = True


class Database:
    def __init__(self):
        self.server = self._get_required_env("DB_SERVER")
        self.database = self._get_required_env("DB_NAME")
        self.user = self._get_required_env("DB_USER")
        self.password = self._get_required_env("DB_PASSWORD")

        self.conn_str = (
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server={self.server};"
            f"Database={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=5;"
        )

        logger.info("Databázová vrstva inicializována, ODBC pooling je zapnutý")

    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Chybí povinná proměnná prostředí: {key}")
        return value

    def _connect(self):
        logger.debug("Vytvářím databázové spojení")
        return pyodbc.connect(self.conn_str)

    def execute(self, query: str, params: tuple = ()):
        logger.info("Provádím SQL dotaz s parametry: %s", params)

        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall()
                    logger.info("SQL dotaz proběhl úspěšně, načteno %d řádků", len(rows))
                    return rows

        except pyodbc.Error:
            logger.exception("Chyba při komunikaci s databází")
            raise