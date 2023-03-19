import sqlalchemy
import databases


DATABASE_URL = 'postgresql://gena:123456@ddb:5432/bet'
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
