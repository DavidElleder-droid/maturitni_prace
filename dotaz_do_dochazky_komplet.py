import argparse
import pyodbc   

SERVER = r"10.0.0.4"          
DATABASE = "dochazka"         

User = "cipovani"
login = "xBLwCB2wd"


conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server={SERVER};"
    f"Database={DATABASE};"
    f"UID={User};"
    f"PWD={login};"
    "Encrypt=optional;"
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
WHERE o.jmeno = ? AND o.prijmeni = ?
ORDER BY p.datum DESC, p.CAS DESC;
"""

def print_rows(rows):
    if not rows:
        print("Nebyly nalezeny žádné záznamy.")
        return

    print(f"{'Datum':10} {'Čas':8} {'Jméno':10} {'Příjmení':12} {'Čip':8} {'OsobaID':12}")
    print("-" * 70)
    for r in rows:
        print(
            f"{r.datum:%Y-%m-%d} "
            f"{str(r.cas)[:8]:8} "
            f"{r.jmeno:10} "
            f"{r.prijmeni:12} "
            f"{str(r.cip):8} "
            f"{str(r.osoba_id):12} "
        )


def main():
    parser = argparse.ArgumentParser(
        description="CLI nástroj pro dotazování docházkové databáze."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--date",
        help="Vyhledá průchody podle data (YYYY-MM-DD)"
    )
    group.add_argument(
        "--person",
        nargs=2,
        metavar=("JMENO", "PRIJMENI"),
        help="Vyhledá průchody konkrétní osoby"
    )

    args = parser.parse_args()

    try:
        conn = pyodbc.connect(conn_str)
    except Exception as e:
        print("CHYBA při připojení k databázi:")
        print(e)
        return

    cur = conn.cursor()

    if args.date:
        print(f"Hledám průchody pro datum: {args.date}\n")
        cur.execute(QUERY_BY_DATE, args.date)
    elif args.person:
        jmeno, prijmeni = args.person
        print(f"Hledám průchody pro osobu: {jmeno} {prijmeni}\n")
        cur.execute(QUERY_BY_PERSON, jmeno, prijmeni)

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
