import logging
import os

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
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Chybí povinná proměnná prostředí: {key}")
    return value


BASE_URL = get_required_env("BASE_URL")
API_KEY = get_required_env("API_KEY")

mcp = FastMCP("dochazka")


def get_headers() -> dict:
    return {"X-API-Key": API_KEY}


def handle_response(response: requests.Response):
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


@mcp.tool()
def get_passes_by_date(date: str, limit: int = 100, offset: int = 0):
    """Vrátí průchody pro zadané datum ve formátu YYYY-MM-DD."""
    logger.info(
        "MCP volání get_passes_by_date | date=%s | limit=%s | offset=%s",
        date,
        limit,
        offset
    )

    try:
        response = requests.get(
            f"{BASE_URL}/passes/by-date",
            params={
                "date": date,
                "limit": limit,
                "offset": offset
            },
            headers=get_headers(),
            timeout=10
        )
        result = handle_response(response)
        logger.info("MCP get_passes_by_date dokončeno")
        return result

    except requests.RequestException as e:
        logger.exception("Síťová chyba při MCP volání get_passes_by_date")
        return {
            "error": "Nelze se spojit s API.",
            "detail": str(e)
        }


@mcp.tool()
def get_passes_by_person(
    first_name: str,
    last_name: str,
    limit: int = 100,
    offset: int = 0
):
    """Vrátí průchody pro zadanou osobu."""
    logger.info(
        "MCP volání get_passes_by_person | first_name=%s | last_name=%s | limit=%s | offset=%s",
        first_name,
        last_name,
        limit,
        offset
    )

    try:
        response = requests.get(
            f"{BASE_URL}/passes/by-person",
            params={
                "first_name": first_name,
                "last_name": last_name,
                "limit": limit,
                "offset": offset
            },
            headers=get_headers(),
            timeout=10
        )
        result = handle_response(response)
        logger.info("MCP get_passes_by_person dokončeno")
        return result

    except requests.RequestException as e:
        logger.exception("Síťová chyba při MCP volání get_passes_by_person")
        return {
            "error": "Nelze se spojit s API.",
            "detail": str(e)
        }


if __name__ == "__main__":
    logger.info("Docházka MCP server started")
    mcp.run()