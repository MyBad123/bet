import sqlalchemy
import databases


DATABASE_URL = 'postgresql://gena:123456@127.0.0.1:5433/bet'
database = databases.Database(DATABASE_URL)


metadata = sqlalchemy.MetaData()

table_events = sqlalchemy.Table(
    'event',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('coefficient', sqlalchemy.Float),
    sqlalchemy.Column('deadline', sqlalchemy.Integer),
    sqlalchemy.Column('state', sqlalchemy.Integer),
)

table_bet = sqlalchemy.Table(
    'user_bet',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('sum_bet', sqlalchemy.Float),
    sqlalchemy.Column('event_id', sqlalchemy.Integer),
    sqlalchemy.Column('result', sqlalchemy.Integer)
)
