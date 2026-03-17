from datetime import date
from typing import List, Optional
import pyodbc
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Docházka API")


SERVER = r"10.0.0.4"
DATABASE = "dochazka"
USER = "cipovani"
PASSWORD = "xBLwCB2wd"

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server={SERVER};"
    f"Database={DATABASE};"
    f"UID={USER};"
    f"PWD={PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


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

#forma vystupu
class PassRecord(BaseModel):
    datum: date
    cas: str
    cip: str
    jmeno: str
    prijmeni: str
    osoba_id: int 

def fetch_rows(query: str, params: tuple) -> List[PassRecord]:
    conn = pyodbc.connect(conn_str)
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()

        out: List[PassRecord] = []
        for r in rows:
            out.append(
                PassRecord(
                    datum=r.datum,
                    cas=str(r.cas)[:8],
                    cip=str(r.cip),
                    jmeno=str(r.jmeno),
                    prijmeni=str(r.prijmeni),
                    osoba_id=r.osoba_id,
                )
            )
        return out
    finally:
        conn.close()



@app.get("/passes/by-date", response_model=List[PassRecord])
def passes_by_date(date_value: date = Query(..., alias="date")):
  
    return fetch_rows(QUERY_BY_DATE, (date_value,))

@app.get("/passes/by-person", response_model=List[PassRecord])
def passes_by_person(first_name: str, last_name: str):
  
    return fetch_rows(QUERY_BY_PERSON, (f"%{first_name}%", f"%{last_name}%"))




# uvicorn api:app --reload
# http://127.0.0.1:8000/docs

