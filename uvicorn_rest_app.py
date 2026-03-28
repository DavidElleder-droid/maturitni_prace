"""
Entrypoint pro spuštění REST API aplikace Docházka přes Uvicorn.

Tento soubor pouze skládá jednotlivé vrstvy aplikace:
- databázovou vrstvu,
- service vrstvu,
- REST server vrstvu.

Spuštění:
    uvicorn uvicorn_rest_app:app --reload
"""

import logging

from db import Database
from dochazka_db_service import DochazkaService
from dochazka_rest_server import DochazkaRestServer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)
logger.info("Spouštím aplikaci Docházka API")

db = Database()
service = DochazkaService(db)
server = DochazkaRestServer(service)

app = server.app

# uvicorn uvicorn_rest_app:app --reload
# http://127.0.0.1:8000/docs