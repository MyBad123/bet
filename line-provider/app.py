import enum
import time
import decimal
from typing import Optional

import asyncpg
import asyncio
import databases
import sqlalchemy
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import table_events


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class Event(BaseModel):
    event_id: int
    coefficient: Optional[decimal.Decimal] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None


class EventCreate(BaseModel):
    coefficient: float
    deadline: int


DATABASE_URL = 'postgresql://gena:123456@ddb:5432/bet'
database = databases.Database(DATABASE_URL)


app = FastAPI()
conn = None

@app.on_event("startup")
async def startup():
    conn = await asyncpg.connect(host='bbd', port=5432, user='gena', password='password', max_inactive_connection_lifetime=3)

@app.on_event("shutdown")
async def shutdown():
    await conn.close()


@app.get('/events')
async def get_events():
    query = sqlalchemy.select(table_events) \
        .where(table_events.c.deadline > time.time())
    return await database.fetch_all(query)


@app.post('/event')
async def create_event(event: EventCreate):
    # control time of event
    if event.deadline < time.time():
        raise HTTPException(
            status_code=400,
            detail="Event has already ended"
        )

    # query for new event object
    query = table_events.insert().values(
        coefficient=event.coefficient,
        deadline=event.deadline,
        state=EventState.NEW.value
    )
    id_new_obj = await database.execute(query)

    # get data of new object
    get_query = sqlalchemy.select(table_events).where(
        table_events.c.id == id_new_obj
    )

    return await database.fetch_all(get_query)


@app.put('/event')
async def update_event(event: Event):
    data_dict = {}
    for name, value in event.dict().items():
        if value is not None:
            data_dict[name] = value

    id_obj = data_dict.pop('event_id')

    # make query for update event
    query = sqlalchemy.update(table_events) \
        .where(table_events.c.id == id_obj) \
        .values(**data_dict)

    await database.execute(query)

    return {}


@app.get('/events/{event_id}')
async def get_event(event_id: int):
    # make query for get event
    query = sqlalchemy.select(table_events) \
        .where(table_events.c.id == event_id)

    # work with query
    data_from_db = await database.fetch_all(query)

    data = {}
    for i in data_from_db:
        data = {
            'id': i.id,
            'coefficient': i.coefficient,
            'deadline': i.deadline,
            'state': i.state
        }

    if data == {}:
        raise HTTPException(
            status_code=404,
            detail='Event is not found'
        )

    return data
