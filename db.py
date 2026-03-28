"""
Databázová vrstva projektu Docházka.

Zajišťuje načtení konfigurace z prostředí, vytvoření připojení
k SQL Serveru a vykonávání parametrizovaných SQL dotazů.
"""


import logging
import os
from typing import TypeAlias

import pyodbc
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Zapnutí ODBC connection poolingu.
# Musí být nastaveno před vytvářením connection.
pyodbc.pooling = True

SQLParam: TypeAlias = str | int | float


class Database:
    """Databázová vrstva zajišťující připojení k SQL Serveru a vykonávání dotazů."""

    def __init__(self) -> None:
        """
        Načte konfiguraci z prostředí a připraví connection string.

        Raises:
            ValueError: Pokud chybí některá povinná proměnná prostředí.
        """
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
        """
        Vrátí hodnotu povinné proměnné prostředí.

        Args:
            key: Název proměnné prostředí.

        Returns:
            Hodnota proměnné prostředí.

        Raises:
            ValueError: Pokud proměnná není nastavena.
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Chybí povinná proměnná prostředí: {key}")
        return value

    def _connect(self) -> pyodbc.Connection:
        """
        Vytvoří nové databázové spojení.

        Returns:
            Otevřené spojení k SQL Serveru.
        """
        logger.debug("Vytvářím databázové spojení")
        return pyodbc.connect(self.conn_str)

    def execute(self, query: str, params: tuple[SQLParam, ...] = ()) -> list[pyodbc.Row]:
        """
        Provede SQL dotaz a vrátí všechny načtené řádky.

        Args:
            query: SQL dotaz, který se má vykonat.
            params: Parametry předané do SQL dotazu.

        Returns:
            Seznam řádků vrácených databází.

        Raises:
            pyodbc.Error: Pokud dojde k chybě při komunikaci s databází.
        """
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