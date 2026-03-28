# Docházkový systém – maturitní práce

## Popis projektu

Tento projekt představuje jednoduchý docházkový systém postavený nad existující databází školy.  
Umožňuje vyhledávat záznamy o průchodech osob podle data nebo podle jména a příjmení.

Cílem práce bylo vytvořit přehledné REST API nad databází a ukázat základní principy backendového vývoje:

- rozdělení aplikace do vrstev
- práce s databází
- autentizace pomocí API klíče
- error handling
- propojení s AI nástrojem pomocí MCP

---

## Funkce systému

API umožňuje:

- vyhledání průchodů podle data
- vyhledání průchodů podle osoby (jméno + příjmení)

Každý záznam obsahuje:

- datum
- čas
- čip
- jméno
- příjmení
- ID osoby

Dále systém podporuje:

- stránkování (`limit`, `offset`)
- autentizaci pomocí API klíče
- základní error handling

---

## Architektura projektu

Projekt je rozdělen do několika vrstev:

### `db.py`
Databázová vrstva.  
Zajišťuje připojení k SQL Serveru a vykonávání SQL dotazů.

---

### `dochazka_db_service.py`
Service vrstva.  
Obsahuje aplikační logiku a převádí databázové řádky na výstupní modely (`PassRecord`).

---

### `dochazka_rest_server.py`
REST vrstva postavená nad FastAPI.  
Zpracovává HTTP požadavky, validuje API klíč a volá service vrstvu.

---

### `uvicorn_rest_app.py`
Entrypoint aplikace.  
Skládá jednotlivé vrstvy dohromady a vystavuje FastAPI aplikaci.

---

### `mcp_server.py`
MCP vrstva.  
Obsahuje klienta (`DochazkaMcpClient`), který komunikuje s REST API pomocí HTTP.

---

### `mcp_server_main.py`
Entrypoint MCP serveru.  
Spouští MCP server pro použití v AI nástrojích (např. Claude Desktop).

---

## Použité technologie

- Python
- FastAPI
- Uvicorn
- pyodbc
- Microsoft SQL Server
- Pydantic
- requests
- FastMCP
- python-dotenv

---

## Konfigurace

V kořenové složce projektu vytvoř `.env` soubor:

```env
DB_SERVER=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
API_KEY=...
BASE_URL=http://127.0.0.1:8000
````

Soubor `.env` není součástí repozitáře.

---

## Instalace závislostí

Pomocí Makefile:

```bash
make prepare
```

Nebo ručně:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

---

## Spuštění REST API

```bash
make start-web-server
```

Nebo ručně:

```bash
python -m uvicorn uvicorn_rest_app:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## Endpointy

### GET `/passes/by-date`

Parametry:

* `date` (YYYY-MM-DD)
* `limit`
* `offset`

---

### GET `/passes/by-person`

Parametry:

* `first_name`
* `last_name`
* `limit`
* `offset`

---

## Autentizace

API používá API klíč.

Posílá se v HTTP hlavičce:

```
X-API-Key: tvuj_klic
```

Bez správného klíče server vrací chybu `401 Unauthorized`.

---

## Error handling

API vrací tyto chyby:

* `401` – neplatný API klíč
* `503` – databáze nedostupná
* `500` – interní chyba

---

## MCP a AI integrace

Projekt lze propojit s AI nástroji pomocí MCP serveru.

Ukázka konfigurace (Claude Desktop):

```json
{
  "mcpServers": {
    "dochazka": {
      "command": "python",
      "args": [
        "C:\\Users\\delle\\OneDrive\\Dokumenty\\maturitní práce\\mcp_server_main.py"
      ]
    }
  }
}
```

MCP server následně volá REST API a vrací výsledky modelu.

---

## Spuštění MCP serveru

```bash
make start-mcp-server
```

Nebo:

```bash
python mcp_server_main.py
```

---

## Databáze

* datum je uložen jako počet dnů od `1900-01-01`
* převod probíhá v aplikaci
* používá se stránkování (`OFFSET`, `FETCH`)
* dotazy jsou optimalizované pro indexy

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

Projekt představuje ukázku vícevrstvé backendové aplikace:

* databázová vrstva
* service vrstva
* REST API
* autentizace
* error handling
* propojení s AI pomocí MCP