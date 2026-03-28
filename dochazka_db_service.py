"""
Service vrstva projektu Docházka.

Obsahuje aplikační logiku pro načítání docházkových záznamů
z databáze a jejich převod na výstupní modely.
"""


from datetime import date

import pyodbc
from pydantic import BaseModel

from db import Database, SQLParam


class ServiceError(Exception):
    """Obecná chyba aplikační/service vrstvy."""


class DatabaseUnavailableError(ServiceError):
    """Databáze je nedostupná nebo došlo k chybě při dotazu."""


class PassRecord(BaseModel):
    """Výstupní model jednoho průchodu osoby docházkovým systémem."""

    datum: date
    cas: str
    cip: str
    jmeno: str
    prijmeni: str
    osoba_id: int


class DochazkaService:
    """Service vrstva pro čtení docházkových záznamů z databáze."""

    QUERY_BY_DATE = """
    SELECT
        DATEADD(DAY, p.datum, '1900-01-01') AS datum,
        CONVERT(time, DATEADD(SECOND, p.CAS, 0)) AS cas,
        p.cip,
        o.jmeno,
        o.prijmeni,
        o.id AS osoba_id
    FROM dbo.pruchod p
    JOIN dbo.osoby o ON p.cip = o.cip
    WHERE p.datum = ?
    ORDER BY p.datum DESC, p.CAS DESC
    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;
    """

    QUERY_BY_PERSON = """
    SELECT
        DATEADD(DAY, p.datum, '1900-01-01') AS datum,
        CONVERT(time, DATEADD(SECOND, p.CAS, 0)) AS cas,
        p.cip,
        o.jmeno,
        o.prijmeni,
        o.id AS osoba_id
    FROM dbo.pruchod p
    JOIN dbo.osoby o ON p.cip = o.cip
    WHERE o.jmeno = ?
    AND o.prijmeni = ?
    ORDER BY p.datum DESC, p.CAS DESC
    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;
    """

    def __init__(self, db: Database) -> None:
        """
        Inicializuje service vrstvu.

        Args:
            db: Databázová vrstva zajišťující vykonávání SQL dotazů.
        """
        self.db = db

    def _date_to_db_days(self, date_value: date) -> int:
        """
        Převede datum na počet dnů od 1900-01-01.

        Args:
            date_value: Datum zadané klientem.

        Returns:
            Počet dnů od základního data používaného v databázi.
        """
        base_date = date(1900, 1, 1)
        return (date_value - base_date).days

    def _fetch_rows(self, query: str, params: tuple[SQLParam, ...]) -> list[PassRecord]:
        """
        Provede SQL dotaz a převede vrácené řádky na seznam modelů PassRecord.

        Args:
            query: SQL dotaz, který se má provést.
            params: Parametry předané do SQL dotazu.

        Returns:
            Seznam nalezených průchodů.

        Raises:
            DatabaseUnavailableError: Pokud dojde k chybě komunikace s databází.
        """
        try:
            rows = self.db.execute(query, params)
        except pyodbc.Error as e:
            raise DatabaseUnavailableError(
                "Nepodařilo se načíst data z databáze."
            ) from e

        result: list[PassRecord] = []

        for row in rows:
            result.append(
                PassRecord(
                    datum=row.datum,
                    cas=str(row.cas)[:8],
                    cip=str(row.cip),
                    jmeno=str(row.jmeno).strip(),
                    prijmeni=str(row.prijmeni).strip(),
                    osoba_id=row.osoba_id,
                )
            )

        return result

    def get_passes_by_date(
        self,
        date_value: date,
        limit: int = 100,
        offset: int = 0
    ) -> list[PassRecord]:
        """
        Vrátí průchody pro zadané datum.

        Args:
            date_value: Hledané datum.
            limit: Maximální počet vrácených záznamů.
            offset: Počet přeskočených záznamů pro stránkování.

        Returns:
            Seznam průchodů odpovídajících zadanému datu.
        """
        db_days = self._date_to_db_days(date_value)
        return self._fetch_rows(self.QUERY_BY_DATE, (db_days, offset, limit))

    def get_passes_by_person(
        self,
        first_name: str,
        last_name: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[PassRecord]:
        """
        Vrátí průchody pro zadanou osobu podle jména a příjmení.

        Args:
            first_name: Jméno osoby.
            last_name: Příjmení osoby.
            limit: Maximální počet vrácených záznamů.
            offset: Počet přeskočených záznamů pro stránkování.

        Returns:
            Seznam průchodů odpovídajících zadané osobě.
        """
        first_name_clean = first_name.strip()
        last_name_clean = last_name.strip()

        return self._fetch_rows(
            self.QUERY_BY_PERSON,
            (first_name_clean, last_name_clean, offset, limit)
        )