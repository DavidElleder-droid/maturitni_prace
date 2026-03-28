prepare:
	python -m venv .venv
	.venv\Scripts\python -m pip install --upgrade pip
	.venv\Scripts\python -m pip install -r requirements.txt

start-web-server:
	.venv\Scripts\python -m uvicorn uvicorn_rest_app:app --reload

start-mcp-server:
	.venv\Scripts\python mcp_server_main.py