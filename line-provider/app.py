import enum
import time
import decimal
from typing import Optional

import httpx
import asyncio
import asyncpg
import databases
import sqlalchemy
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import table_events
from update_query_class import QueryUpdate


class Event(BaseModel):
    event_id: int
    state: int


class EventCreate(BaseModel):
    coefficient: float
    deadline: int


DATABASE_URL = 'postgresql://gena:123456@ddb:5432/bet'
database = databases.Database(DATABASE_URL)


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


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
        state=1
    )
    id_new_obj = await database.execute(query)

    # get data of new object
    get_query = sqlalchemy.select(table_events).where(
        table_events.c.id == id_new_obj
    )

    return await database.fetch_all(get_query)


@app.put('/event')
async def update_event(event: Event):

    # get users_data
    users_data = {}
    for name, value in event.dict().items():
        if value is not None:
            users_data[name] = value

    user_id_obj = users_data.pop('event_id')

    update_class = QueryUpdate(
        users_data=users_data,
        user_id_obj=user_id_obj,
        db=database
    )

    control_update_class: dict = await update_class.control_error()
    if control_update_class.get('status'):
        raise HTTPException(
            status_code=400,
            detail=control_update_class.get('detail')
        )

    # make query for update event
    query = sqlalchemy.update(table_events) \
        .where(table_events.c.id == user_id_obj) \
        .values(**users_data)

    await database.execute(query)

    # update bets update-bet
    async with httpx.AsyncClient() as client:
        r = await client.put('http://bet-maker:8000/update-bet', json={
            'id_event': user_id_obj,
            'status': users_data.get('state')
        })
        print(r.status_code)


    # get new data
    query = sqlalchemy.select(table_events) \
        .where(table_events.c.id == user_id_obj)

    return await database.fetch_all(query)


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
