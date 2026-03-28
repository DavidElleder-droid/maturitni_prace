"""
REST server projektu Docházka postavený nad FastAPI.

Soubor obsahuje třídu DochazkaServer, která:
- vytváří FastAPI aplikaci,
- registruje endpointy,
- ověřuje API klíč,
- převádí chyby service vrstvy na HTTP odpovědi.
"""


import logging
import os
from collections.abc import Callable
from datetime import date
from typing import TypeVar

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query

from dochazka_db_service import (
    DatabaseUnavailableError,
    DochazkaService,
    PassRecord,
    ServiceError,
)

load_dotenv()

logger = logging.getLogger(__name__)


T = TypeVar("T")


class DochazkaRestServer:
    """REST vrstva aplikace Docházka postavená nad FastAPI."""

    def __init__(self, service: DochazkaService) -> None:
        """
        Inicializuje REST server a zaregistruje endpointy.

        Args:
            service: Service vrstva zajišťující práci s docházkovými daty.

        Raises:
            ValueError: Pokud není nastavena povinná proměnná prostředí API_KEY.
        """
        self.service = service
        self.app = FastAPI(title="Docházka API")
        self.api_key = os.getenv("API_KEY")

        if not self.api_key:
            logger.error("API_KEY není nastaven v .env")
            raise ValueError("Chybí povinná proměnná prostředí: API_KEY")

        self._register_routes()

    def _check_api_key(self, x_api_key: str | None) -> None:
        """
        Ověří API klíč zaslaný klientem v HTTP hlavičce.

        Args:
            x_api_key: Hodnota hlavičky X-API-Key.

        Raises:
            HTTPException: Pokud je API klíč neplatný nebo chybí.
        """
        if x_api_key != self.api_key:
            logger.warning("Neplatný nebo chybějící API key")
            raise HTTPException(
                status_code=401,
                detail="Neplatný nebo chybějící API klíč."
            )

    def _handle_service_call(self, func: Callable[[], T]) -> T:
        """
        Obalí volání service vrstvy a převádí interní chyby na HTTP odpovědi.

        Args:
            func: Funkce bez parametrů, která provede konkrétní service operaci.

        Returns:
            Výsledek vrácený service vrstvou.

        Raises:
            HTTPException: Pokud dojde k chybě při zpracování požadavku.
        """
        try:
            return func()
        except DatabaseUnavailableError:
            logger.exception("Databáze je nedostupná nebo došlo k chybě při dotazu")
            raise HTTPException(
                status_code=503,
                detail="Databáze je momentálně nedostupná."
            ) from None
        except ServiceError as e:
            logger.exception("Chyba service vrstvy")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            ) from None
        except HTTPException:
            raise
        except Exception:
            logger.exception("Neočekávaná chyba při zpracování požadavku")
            raise HTTPException(
                status_code=500,
                detail="Došlo k neočekávané chybě serveru."
            ) from None

    def _register_routes(self) -> None:
        """Zaregistruje REST endpointy aplikace."""

        @self.app.get("/passes/by-date", response_model=list[PassRecord])
        def passes_by_date(
            date_value: date = Query(..., alias="date"),
            limit: int = Query(100, ge=1, le=500),
            offset: int = Query(0, ge=0),
            x_api_key: str | None = Header(None, alias="X-API-Key")
        ) -> list[PassRecord]:
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

        @self.app.get("/passes/by-person", response_model=list[PassRecord])
        def passes_by_person(
            first_name: str,
            last_name: str,
            limit: int = Query(100, ge=1, le=500),
            offset: int = Query(0, ge=0),
            x_api_key: str | None = Header(None, alias="X-API-Key")
        ) -> list[PassRecord]:
            logger.info(
                "HTTP GET /passes/by-person | first_name=%s | last_name=%s | limit=%s | offset=%s",
                first_name,
                last_name,
                limit,
                offset
            )
            self._check_api_key(x_api_key)
            return self._handle_service_call(
                lambda: self.service.get_passes_by_person(
                    first_name,
                    last_name,
                    limit,
                    offset
                )
            )