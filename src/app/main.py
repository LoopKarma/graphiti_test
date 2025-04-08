#!/usr/bin/env python3
import logging
import os
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from datetime import datetime
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.sleep(10)
    graphiti = Graphiti(os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
    await graphiti.build_indices_and_constraints()

    app.state.graphiti = graphiti
    yield
    await graphiti.close()


fast_api_app = FastAPI(
    title="graphiti",
    version="0.10",
    description="Zep Graphiti",
    lifespan=lifespan
)


@fast_api_app.get("/internal/health")
def internal_health():
    logging.debug("Health check endpoint called")
    return {"status": "ok"}


@fast_api_app.get("/internal/ready")
def internal_ready():
    logging.debug("Readiness check endpoint called")
    return {"status": "ok"}


def get_files_from_directory(directory_path: str) -> list[str]:
    absolute_directory_path = Path(__file__).parent.parent / Path('data') / Path(directory_path)
    if not absolute_directory_path.exists():
        raise ValueError(f"Directory {directory_path} is not found")

#     return full file path for each file in the directory
    return [str(file) for file in absolute_directory_path.iterdir() if file.is_file()]

def get_file_pointer(file_path: str):
    absolute_file_path = Path(__file__).parent.parent / Path('data') / Path(file_path)
    if not absolute_file_path.exists():
        raise ValueError(f"File {file_path} is not found")

    return absolute_file_path.open('r')


@fast_api_app.get("/add_text_episodes_from_file")
async def add_text_from_file(file_name: str, request: Request):
    with get_file_pointer(f"text/{file_name}") as file_pointer:
        content = file_pointer.read()
        graphiti = request.app.state.graphiti

        await graphiti.add_episode(
            name=file_name,
            episode_body=content,
            source=EpisodeType.text,
            source_description='',
            group_id=file_name,
            reference_time=datetime.now(),
        )

@fast_api_app.get("/add_all_text_episodes")
async def add_text_from_file(request: Request):
    graphiti = request.app.state.graphiti
    for file in get_files_from_directory("text"):
        with open(file, 'r') as file_pointer:
            content = file_pointer.read()
            # get last part of the file path as the name
            file_name = file.split('/')[-1]
            await graphiti.add_episode(
                name=file_name,
                episode_body=content,
                source=EpisodeType.text,
                source_description='',
                group_id=file_name,
                reference_time=datetime.now(),
            )


@fast_api_app.get("/add_json_episodes_from_file")
async def add_json_from_file(file_name: str, request: Request):
    with get_file_pointer(f"json/{file_name}") as file_pointer:
        content = json.load(file_pointer)
        graphiti = request.app.state.graphiti

        for item, episode in enumerate(content):
            await graphiti.add_episode(
                name=f"{file_name}_{item}",
                episode_body=item,
                source=EpisodeType.json,
                source_description='',
                group_id=file_name,
                reference_time=datetime.now(),
            )


@fast_api_app.get("/add_conversation_episode_from_file")
async def add_conversation_from_file(file_name: str, request: Request):
    with get_file_pointer(f"conversation/{file_name}") as file_pointer:
        content = file_pointer.read()
        graphiti = request.app.state.graphiti

        await graphiti.add_episode(
            name=file_name,
            episode_body=content,
            source=EpisodeType.message,
            source_description='',
            group_id=file_name,
            reference_time=datetime.now(),
        )


@fast_api_app.get("/build_community")
async def build_community(request: Request):
    graphiti = request.app.state.graphiti
    await graphiti.build_communities([
        '0060-api-gateway-approach.md',
        '0060-use-string-keys-for-kafka-messages.md',
        '0061-prefer-cursor-based-pagination-for-apis.md',
        '0062-prefer-cursor-based-pagination-for-database-queries.md',
        '0063-mcp-servers-in-python.md',
        '0064-how-we-do-cronjobs.md',
    ])


if __name__ == "__main__":
    import uvicorn

    # Configure uvicorn to use our logger
    uvicorn.run(
        fast_api_app,
        host="0.0.0.0",
        port=8080,
        loop="asyncio",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
