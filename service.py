from datetime import date
from typing import List

import pyodbc
from pydantic import BaseModel

from db import Database


class ServiceError(Exception):
    """Obecná chyba aplikační/service vrstvy."""
    pass


class DatabaseUnavailableError(ServiceError):
    """Databáze je nedostupná nebo došlo k chybě při dotazu."""
    pass


class PassRecord(BaseModel):
    datum: date
    cas: str
    cip: str
    jmeno: str
    prijmeni: str
    osoba_id: int


class DochazkaService:
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

    def __init__(self, db: Database):
        self.db = db

    def _date_to_db_days(self, date_value: date) -> int:
        base_date = date(1900, 1, 1)
        return (date_value - base_date).days

    def _fetch_rows(self, query: str, params: tuple) -> List[PassRecord]:
        try:
            rows = self.db.execute(query, params)
        except pyodbc.Error as e:
            raise DatabaseUnavailableError("Nepodařilo se načíst data z databáze.") from e

        result: List[PassRecord] = []

        for r in rows:
            result.append(
                PassRecord(
                    datum=r.datum,
                    cas=str(r.cas)[:8],
                    cip=str(r.cip),
                    jmeno=str(r.jmeno).strip(),
                    prijmeni=str(r.prijmeni).strip(),
                    osoba_id=r.osoba_id,
                )
            )

        return result

    def get_passes_by_date(self, date_value: date, limit: int = 100, offset: int = 0) -> List[PassRecord]:
        db_days = self._date_to_db_days(date_value)
        return self._fetch_rows(self.QUERY_BY_DATE, (db_days, offset, limit))

    def get_passes_by_person(self, first_name: str, last_name: str, limit: int = 100, offset: int = 0) -> List[PassRecord]:
        first_name_clean = first_name.strip()
        last_name_clean = last_name.strip()

        return self._fetch_rows(
            self.QUERY_BY_PERSON,
            (first_name_clean, last_name_clean, offset, limit)
        )