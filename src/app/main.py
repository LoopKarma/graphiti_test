#!/usr/bin/env python3
import logging
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import asyncio
# Load environment variables first to ensure logging has access to variables
load_dotenv()

from time import sleep
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Building indices and constraints")
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


@fast_api_app.post("/")
async def istio_health(request: Request):
    graphiti = request.app.state.graphiti
    episodes = [
        "Kamala Harris is the Attorney General of California. She was previously "
        "the district attorney for San Francisco.",
        "As AG, Harris was in office from January 3, 2011 – January 3, 2017",
    ]
    for i, episode in enumerate(episodes):
        await graphiti.add_episode(
            name=f"Freakonomics Radio {i}",
            episode_body=episode,
            source=EpisodeType.text,
            source_description="podcast",
            reference_time=datetime.now()
        )

    return {"status": "ok"}



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
