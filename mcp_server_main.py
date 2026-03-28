"""
Entrypoint pro spuštění MCP serveru Docházka.

Tento soubor obsahuje pouze startovací kód.
Samotná definice MCP nástrojů a logika komunikace s REST API
jsou umístěny v souboru mcp_server.py.

Spuštění:
    python mcp_server_main.py
"""


from mcp_server import logger, mcp


if __name__ == "__main__":
    logger.info("Docházka MCP server started")
    mcp.run()