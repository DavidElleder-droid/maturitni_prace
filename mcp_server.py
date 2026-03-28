"""
MCP vrstva projektu Docházka.

Soubor obsahuje:
- načtení konfiguračních proměnných,
- klienta pro komunikaci s REST API,
- definici MCP nástrojů pro vyhledávání průchodů.

MCP server nekomunikuje přímo s databází, ale volá REST API.
"""



import logging
import os
from typing import TypeAlias

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


def get_required_env(key: str) -> str:
    """
    Vrátí hodnotu povinné proměnné prostředí.

    Args:
        key: Název proměnné prostředí.

    Returns:
        Hodnota proměnné prostředí.

    Raises:
        ValueError: Pokud proměnná prostředí není nastavena.
    """
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Chybí povinná proměnná prostředí: {key}")
    return value


ApiItem: TypeAlias = dict[str, object]
ApiResponse: TypeAlias = ApiItem | list[ApiItem]

class DochazkaMcpClient:
    """Klient zajišťující komunikaci MCP vrstvy s REST API Docházky."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """
        Inicializuje MCP klienta.

        Args:
            base_url: Základní URL REST API.
            api_key: API klíč pro autentizaci vůči REST API.
        """
        self.base_url = base_url
        self.api_key = api_key

    def get_headers(self) -> dict[str, str]:
        """
        Vytvoří HTTP hlavičky pro volání REST API.

        Returns:
            Slovník s autentizační hlavičkou.
        """
        return {"X-API-Key": self.api_key}

    def handle_response(self, response: requests.Response) -> ApiResponse:
        """
        Zpracuje odpověď REST API.

        Args:
            response: HTTP odpověď z REST API.

        Returns:
            JSON data z API nebo strukturovanou chybu.
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError:
            try:
                data = response.json()
                return {
                    "error": data.get("detail", "Neznámá chyba API."),
                    "status_code": response.status_code
                }
            except Exception:
                return {
                    "error": f"HTTP chyba {response.status_code}",
                    "status_code": response.status_code
                }

    def get_passes_by_date(self, date: str, limit: int = 100, offset: int = 0) -> ApiResponse:
        """
        Vrátí průchody pro zadané datum.

        Args:
            date: Datum ve formátu YYYY-MM-DD.
            limit: Maximální počet vrácených záznamů.
            offset: Počet přeskočených záznamů.

        Returns:
            JSON odpověď z REST API nebo chybová struktura.
        """
        logger.info(
            "MCP volání get_passes_by_date | date=%s | limit=%s | offset=%s",
            date,
            limit,
            offset
        )

        try:
            response = requests.get(
                f"{self.base_url}/passes/by-date",
                params={
                    "date": date,
                    "limit": limit,
                    "offset": offset
                },
                headers=self.get_headers(),
                timeout=10
            )
            result = self.handle_response(response)
            logger.info("MCP get_passes_by_date dokončeno")
            return result
        except requests.RequestException as e:
            logger.exception("Síťová chyba při MCP volání get_passes_by_date")
            return {
                "error": "Nelze se spojit s API.",
                "detail": str(e)
            }

    def get_passes_by_person(
        self,
        first_name: str,
        last_name: str,
        limit: int = 100,
        offset: int = 0
    ) -> ApiResponse:
        """
        Vrátí průchody pro zadanou osobu.

        Args:
            first_name: Jméno osoby.
            last_name: Příjmení osoby.
            limit: Maximální počet vrácených záznamů.
            offset: Počet přeskočených záznamů.

        Returns:
            JSON odpověď z REST API nebo chybová struktura.
        """
        logger.info(
            "MCP volání get_passes_by_person | first_name=%s | last_name=%s | limit=%s | offset=%s",
            first_name,
            last_name,
            limit,
            offset
        )

        try:
            response = requests.get(
                f"{self.base_url}/passes/by-person",
                params={
                    "first_name": first_name,
                    "last_name": last_name,
                    "limit": limit,
                    "offset": offset
                },
                headers=self.get_headers(),
                timeout=10
            )
            result = self.handle_response(response)
            logger.info("MCP get_passes_by_person dokončeno")
            return result
        except requests.RequestException as e:
            logger.exception("Síťová chyba při MCP volání get_passes_by_person")
            return {
                "error": "Nelze se spojit s API.",
                "detail": str(e)
            }


mcp = FastMCP("dochazka")

client = DochazkaMcpClient(
    base_url=get_required_env("BASE_URL"),
    api_key=get_required_env("API_KEY")
)


@mcp.tool()
def get_passes_by_date(date: str, limit: int = 100, offset: int = 0) -> ApiResponse:
    """MCP tool pro získání průchodů podle data."""
    return client.get_passes_by_date(date, limit, offset)


@mcp.tool()
def get_passes_by_person(
    first_name: str,
    last_name: str,
    limit: int = 100,
    offset: int = 0
) -> ApiResponse:
    """MCP tool pro získání průchodů podle osoby."""
    return client.get_passes_by_person(first_name, last_name, limit, offset)