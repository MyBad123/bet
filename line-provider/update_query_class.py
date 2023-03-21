import sqlalchemy

from db import table_events


class QueryUpdate:
    select_data: list

    def __init__(self, users_data, user_id_obj, db):
        self.users_data: dict = users_data
        self.user_id_obj: int = user_id_obj
        self.db = db

    async def control_users_data(self) -> bool:
        # get data by id from db
        query: sqlalchemy.sql.selectable.Select = sqlalchemy.select(table_events) \
            .where(table_events.c.id == self.user_id_obj)

        self.select_data = await self.db.fetch_all(query)

        # control find
        control_int: int = 0
        for i in self.select_data:
            control_int += 1

        if control_int == 0:
            return False

        # control state
        control_state: int = 0
        for i in range(1, 4):
            if i == self.users_data.get('state'):
                control_state += 1

        if control_state == 0:
            return False

        return True

    async def control_db_data(self):
        """control data from db object"""

        if self.select_data[0]['state'] != 1:
            return False

        return True

    async def control_error(self):
        """control db data and user's data"""

        control_user_result = await self.control_users_data()
        if not control_user_result:
            return {
                'status': True,
                'detail': 'error in user s data'
            }

        control_db_result = await self.control_db_data()
        if not control_db_result:
            return {
                'status': True,
                'detail': 'error in changing db data'
            }

        return {'status': False}

    async def get_user_data(self):
        """get data of user"""

        return self.users_data
