"""Orchestration App for Screenshots Crawling."""

import asyncio
import contextlib
import os
import subprocess
import sys
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from sqlmodel import create_engine, SQLModel, Field, Session, select


# Pydantic models ...
class FetchParams(BaseModel):
    start_url: str
    number_of_links: int


# SQL Models ...
DATABASE_FILENAME = "../db/screenshots.db"
DATABASE_URL = f"sqlite:///./{DATABASE_FILENAME}"

database_engine = create_engine(DATABASE_URL)

class Screenshot(SQLModel, table=True):
    """Screenshot Class"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    start_url: str
    number_of_links: int


# FastAPI ...
app = FastAPI()
process = None

async def take_screenshots_puppeteer(start_url: str, number_of_links: int) -> str:
    global process

    unique_id = str(uuid.uuid4())
    process = await asyncio.create_subprocess_exec(
        "node",
        "puppeteer_take_screenshots.js",
        unique_id,
        start_url,
        str(number_of_links),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="../nodejs/"
    )
    await process.communicate()
    process = None
    return unique_id


## Endpoints ...
@app.get("/isalive")
async def is_alive():
    """Endpoint: Is Alive"""
    if process:
        return {
            "status": "in_progress",
            "message": "Screenshots are being fetched."
        }
    else:
        return {
            "status": "idle",
            "message": "No processing at the moment."
        }


@app.post("/screenshots", response_model=dict)
async def fetch_screenshots(payload: FetchParams) -> dict:
    """Endpoint: Fetch Screenshots Process"""
    if not payload.start_url or payload.number_of_links <= 0:
        raise HTTPException(status_code=400, detail="Please provide valid start_url and number_of_links")

    unique_id = await take_screenshots_puppeteer(payload.start_url, payload.number_of_links)

    # Commit to DB
    with Session(database_engine) as session:
        screenshot = Screenshot(start_url=payload.start_url, number_of_links=payload.number_of_links)
        session.add(screenshot)
        session.commit()

    return {"id": unique_id}


@app.get("/screenshots/{id}", response_model=List[str])
async def get_screenshots(id: str):
    # Check if the record with the provided ID exists
    with Session(database_engine) as session:
        statement = select(Screenshot).where(Screenshot.id == id)
        screenshot = session.exec(statement)
    
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot ID not found")

    # Define the local relative folder path based on the ID
    screenshots_folder = f"../nodejs/screenshots/{id}"

    # Get a list of image files in the folder
    image_files = []
    for root, _dirs, files in os.walk(screenshots_folder):
        for file in files:
            image_files.append(os.path.join(root, file))

    return image_files


## Events ...
@app.on_event("startup")
def startup_db_client():
    """FastAPI Startup"""
    database_engine.connect()
    SQLModel.metadata.create_all(database_engine)


@app.on_event("shutdown")
def shutdown_db_client():
    """FastAPI Shutdown"""
    database_engine.dispose()