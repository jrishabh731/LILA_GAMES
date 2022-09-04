import json
import logging
import time
import random

from sqlalchemy.orm import Session
from sqlalchemy import and_
from config.db import engine
from fastapi import status, HTTPException

from models.AreaModeEventsSchema import AreaModeEventsAgg, AreaModeEvents
from schema.AreaMode import EventRequestModelIter
from services.RedisHandler import RedisHandler

log = logging.getLogger("API_LOG")


class MultiPlayerModeHandler:
    """
    This class should hold functions to perform the CRUD operations on AreaModeEvents and AreaModeEventsAgg table.
    For usecases like, some other flow needs the AreaMode details for a
    particular idea it can call this fucntion and get the relevant data.
    Similarly all functions should be built in a similar design.
    """

    def __init__(self, session=None):
        # Added session object for easier unittesting.
        self.session = session or Session

    async def get_stats(self, area_code):
        """
        Prepares list of most player mode at the moment for a given areacode.
        1. Fetch data from cache. If exists, then return the response.
        2. If not, then run db query and store the data to redis cache.
        param area_code: Area code for which most players modes are to be prepared.
        :return: {"results": [{"multiplayer_mode": "Temp", "count": 3}]}
        """
        db_results_sorted = {}
        try:
            self.cache = RedisHandler()
            cache_results = await self.cache.get_key(area_code)
            if cache_results:
                log.info(f"Found data for {area_code} in cache.")
                return json.loads(cache_results)
            db_results = None
            with self.session(bind=engine, expire_on_commit=False) as session:
                db_query = session.query(AreaModeEventsAgg).filter(AreaModeEventsAgg.area_code == area_code)
                db_results = db_query.all()

            if db_results is None:
                db_results = []
            if db_results:
                mode_count = [{"count": row.current_count, "multiplayer_mode": row.multiplayer_mode}
                              for row in db_results]
                mode_count.sort(key=lambda k: k.get("count", 0), reverse=True)
                db_results_sorted = {area_code: mode_count}
            await self.cache.set_key(area_code, json.dumps(db_results_sorted), 30)
            log.info(f"Updating cache for area_code {area_code} with {5} sec TTL.")
        except Exception as err:
            log.error(f"Error occured: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Exception occured : {err}",
            ) from err
        log.debug(f"Processed get request for {area_code}, returning response.")
        return db_results_sorted

    def events_handler(self, events):
        """
        Processes events for LOGIN and LOGOUT and updates corresponding records in Aggregate table.
        1. Process each event and create an areacode -> multiplayer mode -> count mapping.
        2. We update db for a given areacode -> multiplayer mode -> current_count to existing_count + current_count
        :param events: EventRequestModelIter obj
        :return: {"status": True}
        :raises: HTTPException
        """
        event_delta_map = {"LOGIN": 1, "LOGOUT": -1}
        event_type = {"LOGIN": [], "LOGOUT": []}
        area_mode_mapping = {}

        for event in events.items:
            event = AreaModeEvents(multiplayer_mode=event.multiplayer_mode, user_id=event.user_id,
                                   area_code=event.area_code, events_name=event.events_name.upper(),
                                   epoch_timestamp=time.time())
            event_type[event.events_name.upper()].append(event)
            delta = event_delta_map[event.events_name.upper()]

            if event.area_code in area_mode_mapping:
                mode_map = area_mode_mapping.get(event.area_code, {})
                if event.multiplayer_mode in mode_map:
                    area_mode_mapping[event.area_code][event.multiplayer_mode] = mode_map[event.multiplayer_mode] \
                                                                                 + delta
                else:
                    area_mode_mapping[event.area_code][event.multiplayer_mode] = delta
            else:
                area_mode_mapping[event.area_code] = {
                    event.multiplayer_mode: delta
                }
        log.info(f"Area and multiplayer mode map : {area_mode_mapping}")
        log.info(f"Count of events for LOGIN: {len(event_type['LOGIN'])} and LOGOUT: {len(event_type['LOGOUT'])}.")

        try:
            with self.session(bind=engine, expire_on_commit=False) as session:
                for event_category in event_type:
                    session.add_all(event_type[event_category])

                for area, mode_values in area_mode_mapping.items():
                    for mode, count in mode_values.items():
                        area_mode_exists = session.query(AreaModeEventsAgg).filter(
                            and_(AreaModeEventsAgg.area_code == area, AreaModeEventsAgg.multiplayer_mode == mode)). \
                            first()
                        if area_mode_exists:
                            log.debug(f"Area: {area} and Mode: {mode} exists in db, updating count.")
                            area_mode_exists.current_count = area_mode_exists.current_count + count
                            session.add(area_mode_exists)
                        else:
                            log.debug(f"Area: {area} and Mode: {mode} doesn't exists in db, creating new record.")
                            session.add(AreaModeEventsAgg(area_code=area, multiplayer_mode=mode, current_count=count))
                session.commit()
            return {"status": True}
        except Exception as err:
            log.error(f"Error occured: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Exception occured : {err}",
            ) from err

    def generate_data(self):
        """
        Generates event for LOGIN/LOGOUT for simulation.
        :return: {"cnt_records_generated": random_record_count}
        """
        # Generate dummy usernames, modes and area codes.
        multiplayer_modes = [f"Modes{i}" for i in range(1, 11)]
        user_names = [f"User{i}" for i in range(1, 11)]
        area_codes = [i for i in range(101, 120)]

        random_record_count = random.randint(500, 1000)
        records = []

        for i in range(random_record_count):
            # Choose random values from the generated dummy data.
            random_mode = random.choice(multiplayer_modes)
            random_user_name = random.choice(user_names)
            random_area_code = random.choice(area_codes)

            records.append({"multiplayer_mode": random_mode, "user_id": random_user_name,
                            "area_code": random_area_code, "events_name": "LOGIN"})

            # Randomly generate LOGOUT events for some LOGIN attempts.
            if random.random() > 0.5:
                records.append({"multiplayer_mode": random_mode, "user_id": random_user_name,
                                "area_code": random_area_code, "events_name": "LOGOUT"})

        self.events_handler(EventRequestModelIter(items=records))
        return {"cnt_records_generated": random_record_count}
