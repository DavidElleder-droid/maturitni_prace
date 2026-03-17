import sys
import requests
from fastmcp import FastMCP 

Base_URL = "http://127.0.0.1:8000"

mcp = FastMCP("dochazka")

@mcp.tool()
def get_passes_by_date (date:str):
    
    # prichody pro dane datum

    r = requests.get(f"{Base_URL}/passes/by-date", params={"date": date})

    r.raise_for_status()
    return r.json()

@mcp.tool()
def get_passes_by_person (first_name:str, last_name:str):
    # prichody pro danou osobu

    r = requests.get(
        f"{Base_URL}/passes/by-person",
        params={
            "first_name": first_name,
            "last_name": last_name
        }
    )

    r.raise_for_status()
    return r.json()

if __name__ == "__main__":  
    print("[MCP] Dochazka MCP server started", file=sys.stderr, flush=True)
    mcp.run()