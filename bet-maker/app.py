import httpx
import databases
import sqlalchemy
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import table_bet, table_events


DATABASE_URL = 'postgresql://gena:123456@ddb:5432/bet'
database = databases.Database(DATABASE_URL)


class NewBet(BaseModel):
    id_event: int
    sum: int


class UpdateBet(BaseModel):
    id_event: int
    status: int


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/events')
async def get_events():
    print('lol1')
    async with httpx.AsyncClient() as client:
        r = await client.get('http://line-provider:8001/events')

    print('lol2')

    return r.json()


@app.post('/bet')
async def create_bet(bet: NewBet):
    # control sum
    if bet.sum < 0:
        raise HTTPException(
            status_code=400,
            detail='Sum < 0'
        )

    # control event
    async with httpx.AsyncClient() as client:
        r = await client.get('http://line-provider:8001/events/' + str(bet.id_event))

    if r.status_code == 200:
        event_data: dict = r.json()
    else:
        raise HTTPException(
            status_code=400,
            detail='event is not found'
        )

    if event_data.get('state') != 1:
        raise HTTPException(
            status_code=400,
            detail='event is not active'
        )

    # create but obj
    query = sqlalchemy.insert(table_bet).values(
        sum_bet=bet.sum,
        event_id=bet.id_event
    )
    await database.execute(query)

    return {}


@app.put('/update-bet')
async def update_status_bet(update_bet: UpdateBet):
    # control status of bet
    control_status: int = 0
    for i in range(1, 4):
        if i == update_bet.status:
            control_status += 1

    if control_status == 0:
        raise HTTPException(
            status_code=400,
            detail='bad status'
        )

    # update result
    query = sqlalchemy.update(table_bet) \
        .where(table_bet.c.event_id == update_bet.id_event) \
        .values(result=update_bet.status)

    await database.execute(query)

    return {}


@app.get('/bets')
async def get_all_bets():
    query = sqlalchemy.select(table_bet)
    return await database.fetch_all(query)
