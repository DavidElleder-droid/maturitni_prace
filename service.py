from datetime import date
from typing import List
from pydantic import BaseModel
from db import get_connection


# výstupní model
class PassRecord(BaseModel):
    datum: date
    cas: str
    cip: str
    jmeno: str
    prijmeni: str
    osoba_id: int


# SQL dotazy date/person
QUERY_BY_DATE = """
SELECT TOP 200
    DATEADD(DAY, p.datum, '1900-01-01') AS datum,
    CONVERT(time, DATEADD(SECOND, p.CAS, 0)) AS cas,
    p.cip,
    o.jmeno,
    o.prijmeni,
    o.id AS osoba_id
FROM dbo.pruchod p
JOIN dbo.osoby o ON p.cip = o.cip
WHERE DATEADD(DAY, p.datum, '1900-01-01') = ?
ORDER BY p.datum DESC, p.CAS DESC;
"""

QUERY_BY_PERSON = """
SELECT TOP 200
    DATEADD(DAY, p.datum, '1900-01-01') AS datum,
    CONVERT(time, DATEADD(SECOND, p.CAS, 0)) AS cas,
    p.cip,
    o.jmeno,
    o.prijmeni,
    o.id AS osoba_id
FROM dbo.pruchod p
JOIN dbo.osoby o ON p.cip = o.cip
WHERE LTRIM(RTRIM(o.jmeno)) LIKE ?
  AND LTRIM(RTRIM(o.prijmeni)) LIKE ?
ORDER BY p.datum DESC, p.CAS DESC;
"""


# obecná funkce
def fetch_rows(query: str, params: tuple) -> List[PassRecord]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()

        result: List[PassRecord] = []

        for r in rows:
            result.append(
                PassRecord(
                    datum=r.datum,
                    cas=str(r.cas)[:8],
                    cip=str(r.cip),
                    jmeno=str(r.jmeno),
                    prijmeni=str(r.prijmeni),
                    osoba_id=r.osoba_id,
                )
            )

        return result
    finally:
        conn.close()


# business logika
def get_passes_by_date(date_value: date) -> List[PassRecord]:
    return fetch_rows(QUERY_BY_DATE, (date_value,))


def get_passes_by_person(first_name: str, last_name: str) -> List[PassRecord]:
    return fetch_rows(
        QUERY_BY_PERSON,
        (f"%{first_name}%", f"%{last_name}%")
    )