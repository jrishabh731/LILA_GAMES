"""
This file will hold the endpoints and there respective handlers.
"""
import logger
import logging
from fastapi import FastAPI, status, Query
from config.db import Base, engine
from handlers.multiplayer_mode_handler import MultiPlayerModeHandler
from schema.AreaMode import EventRequestModelIter


Base.metadata.create_all(engine)

# Create logger object
log = logging.getLogger("API_LOG")
app = FastAPI()


@app.get("/stats/")
async def get_stats(area_code: int = Query(..., ge=100, le=999)):
    """
    Handles stats request and forwards to required controller class.
    """
    handler = MultiPlayerModeHandler()
    return await handler.get_stats(area_code)


@app.post("/events/")
def handle_events(events: EventRequestModelIter):
    """
    Handles LOGIN and LOGOUT events and forwards to required controller class.
    """
    return MultiPlayerModeHandler().events_handler(events)


@app.post("/generate_data/", status_code=status.HTTP_200_OK)
def generate_data():
    """
    Generated random events for simulation.
    """
    return MultiPlayerModeHandler().generate_data()
