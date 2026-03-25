import logging

from db import Database
from service import DochazkaService
from server import DochazkaServer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)
logger.info("Spouštím aplikaci Docházka API")

db = Database()
service = DochazkaService(db)
server = DochazkaServer(service)

app = server.app

# uvicorn main:app --reload
# http://127.0.0.1:8000/docs