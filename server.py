import logging
import os
from datetime import date
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Header, HTTPException

from service import (
    DochazkaService,
    PassRecord,
    DatabaseUnavailableError,
    ServiceError,
)

load_dotenv()

logger = logging.getLogger(__name__)


class DochazkaServer:
    def __init__(self, service: DochazkaService):
        self.service = service
        self.app = FastAPI(title="Docházka API")
        self.api_key = os.getenv("API_KEY")
        self._register_routes()

    def _check_api_key(self, x_api_key: str | None):
        if not self.api_key:
            logger.error("API_KEY není nastaven v .env")
            raise HTTPException(
                status_code=500,
                detail="Server není správně nakonfigurován."
            )

        if x_api_key != self.api_key:
            logger.warning("Neplatný nebo chybějící API key")
            raise HTTPException(
                status_code=401,
                detail="Neplatný nebo chybějící API klíč."
            )

    def _handle_service_call(self, func):
        try:
            return func()
        except DatabaseUnavailableError:
            logger.exception("Databáze je nedostupná nebo došlo k chybě při dotazu")
            raise HTTPException(
                status_code=503,
                detail="Databáze je momentálně nedostupná."
            )
        except ServiceError as e:
            logger.exception("Chyba service vrstvy")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception:
            logger.exception("Neočekávaná chyba při zpracování požadavku")
            raise HTTPException(
                status_code=500,
                detail="Došlo k neočekávané chybě serveru."
            )

    def _register_routes(self):
        @self.app.get("/passes/by-date", response_model=List[PassRecord])
        def passes_by_date(
            date_value: date = Query(..., alias="date"),
            limit: int = Query(100, ge=1, le=500),
            offset: int = Query(0, ge=0),
            x_api_key: str | None = Header(None, alias="X-API-Key")
        ):
            logger.info(
                "HTTP GET /passes/by-date | date=%s | limit=%s | offset=%s",
                date_value,
                limit,
                offset
            )
            self._check_api_key(x_api_key)
            return self._handle_service_call(
                lambda: self.service.get_passes_by_date(date_value, limit, offset)
            )

        @self.app.get("/passes/by-person", response_model=List[PassRecord])
        def passes_by_person(
            first_name: str,
            last_name: str,
            limit: int = Query(100, ge=1, le=500),
            offset: int = Query(0, ge=0),
            x_api_key: str | None = Header(None, alias="X-API-Key")
        ):
            logger.info(
                "HTTP GET /passes/by-person | first_name=%s | last_name=%s | limit=%s | offset=%s",
                first_name,
                last_name,
                limit,
                offset
            )
            self._check_api_key(x_api_key)
            return self._handle_service_call(
                lambda: self.service.get_passes_by_person(first_name, last_name, limit, offset)
            )