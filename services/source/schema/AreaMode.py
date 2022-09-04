from pydantic import BaseModel
from typing import List


class Event(BaseModel):
    area_code: int
    multiplayer_mode: str
    user_id: str
    events_name: str


class EventRequestModelIter(BaseModel):
    items: List[Event] = []

