from datetime import date
from typing import List
from fastapi import FastAPI, Query
from service import get_passes_by_date, get_passes_by_person, PassRecord

app = FastAPI(title="Docházka API")


@app.get("/passes/by-date", response_model=List[PassRecord])
def passes_by_date(date_value: date = Query(..., alias="date")):
    return get_passes_by_date(date_value)


@app.get("/passes/by-person", response_model=List[PassRecord])
def passes_by_person(first_name: str, last_name: str):
    return get_passes_by_person(first_name, last_name)


# uvicorn server:app --reload
# http://127.0.0.1:8000/docs
