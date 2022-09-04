from config.db import Base
from sqlalchemy import Column, String, Integer, BIGINT


class AreaModeEvents(Base):
    __tablename__ = "AreaModeEvents"
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    area_code = Column(Integer, index=True)
    multiplayer_mode = Column(String(255), index=True)
    user_id = Column(String(255))
    events_name = Column(String(255))
    epoch_timestamp = Column(BIGINT)


class AreaModeEventsAgg(Base):
    __tablename__ = "AreaModeEventsAgg"
    area_code = Column(Integer, primary_key=True)
    multiplayer_mode = Column(String(255), primary_key=True)
    current_count = Column(Integer)

