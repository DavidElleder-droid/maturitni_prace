# Docházkový systém – maturitní práce

# Popis projektu

Tento projekt představuje jednoduchý docházkový systém postavený nad existující databází. Umožňuje vyhledávat záznamy o průchodech osob podle data nebo podle jména a příjmení.

Cílem práce bylo vytvořit přehledné API nad databází a ukázat základní principy backendového vývoje – rozdělení aplikace do vrstev, práce s databází, zabezpečení a propojení s AI nástrojem (Claude AI Desktop) pomocí MCP.

---

# Funkce systému

API umožňuje:

* vyhledání průchodů podle data
* vyhledání průchodů podle osoby (jméno a příjmení)

Každý záznam obsahuje:

* datum
* čas
* čip
* jméno a příjmení
* ID osoby

Dále API podporuje:

* stránkování (`limit`, `offset`)
* autentizaci pomocí API klíče
* základní error handling

---

## Architektura

Projekt je rozdělen do několika částí:

* `db.py`
  Zajišťuje připojení k databázi a provádění SQL dotazů.

* `service.py`
  Obsahuje business logiku a SQL dotazy. Převádí data z databáze na výstupní modely.

* `server.py`
  FastAPI vrstva, která vystavuje endpointy. Neobsahuje přímou práci s databází.

* `main.py`
  Skládá aplikaci dohromady a spouští server.

* `mcp_dochazka_server.py`
  MCP server, který komunikuje s API a zpřístupňuje data pro AI nástroje.

---

## Použité technologie

* Python
* FastAPI
* pyodbc
* Microsoft SQL Server
* Pydantic
* requests
* FastMCP
* python-dotenv

---

## Konfigurace

V kořenové složce vytvoř `.env` soubor:

```env
DB_SERVER=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
API_KEY=...
BASE_URL=http://127.0.0.1:8000
```

Soubor `.env` není součástí repozitáře.

---

## Spuštění API

```bash
uvicorn main:app --reload
```

Dokumentace API (Swagger UI):

```
http://127.0.0.1:8000/docs
```

---

## Endpointy

### GET /passes/by-date

Parametry:

* `date` (YYYY-MM-DD)
* `limit` (výchozí 100)
* `offset` (výchozí 0)

---

### GET /passes/by-person

Parametry:

* `first_name`
* `last_name`
* `limit`
* `offset`

---

## Autentizace

API používá jednoduchý API klíč.

Posílá se v hlavičce:

```
X-API-Key: tvuj_klic
```

Bez správného klíče server vrací chybu 401.

---

## Error handling

API vrací základní HTTP chyby:

* 401 – neplatný API klíč
* 503 – databáze není dostupná
* 500 – interní chyba

---

## MCP a Claude Desktop

Projekt je možné propojit s Claude Desktop pomocí MCP.

Konfigurace MCP serveru vypadá například takto:

```json
{
  "mcpServers": {
    "dochazka": {
      "command": "python",
      "args": [
        "C:\\Users\\delle\\OneDrive\\Dokumenty\\maturitní práce\\mcp_dochazka_server.py"
      ]
    }
  }
}
```

Tato konfigurace říká:

* jak se má MCP server spustit
* kde se nachází jeho soubor

Po spuštění Claude Desktop běží MCP server na pozadí a model ho může používat jako nástroj. Server následně volá API a vrací výsledky zpět modelu.

---

## SQL a databáze

* datum je v databázi uložené jako počet dnů od roku 1900
* převod se provádí v aplikaci
* dotazy nepoužívají funkce ve WHERE části, aby bylo možné využít indexy
* používá se stránkování pomocí `OFFSET` a `FETCH`

---

## Databázové připojení

Aplikace používá ODBC connection pooling:

* pro každý dotaz se vytvoří spojení
* po dokončení se zavře
* driver může spojení znovu využít

---

## Logování

Používá se modul `logging`.

Logují se:

* HTTP požadavky
* SQL dotazy
* chyby

Citlivé údaje se nelogují.

---

## Shrnutí

Projekt ukazuje základní principy backendové aplikace:

* rozdělení do vrstev
* práce s databází
* REST API
* autentizace
* error handling
* propojení s AI pomocí MCP

Nejde o produkční systém, ale o funkční a přehlednou ukázku řešení.
