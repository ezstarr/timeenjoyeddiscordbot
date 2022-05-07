import os
import psycopg
from .base_storage import BaseStorage


class PostgresStorage(BaseStorage):

    def __init__(self):
        self._connection: psycopg.Connection = None
        self._connect()
        self._check_tables()

    def _connect(self):
        connection_str = os.getenv('DATABASE_URL')
        self._connection = psycopg.connect(connection_str)
        self._connection.autocommit = True

    def _create_game_states_table(self):
        cursor = self._connection.cursor()
        cursor.execute("create table game_states ( "
                       " game_name varchar(32), "
                       " channel_id bigint, "
                       " game_state text,"
                       " unique (game_name, channel_id) "
                       ");")

        cursor.execute("create unique index idx_game_channel on game_states (game_name, channel_id)")

    def _check_tables(self):
        """
        Check for missing tables and create them if necessary
        :return:
        """
        cursor = self._connection.cursor()
        cursor.execute("select table_name "
                       "from information_schema.tables "
                       "where table_schema='public' "
                       "and table_type='BASE TABLE' ")
        table_names = []
        tables = cursor.fetchall()
        for table in tables:
            table_names.append(table[0])
        if 'game_states' not in table_names:
            self._create_game_states_table()

    def delete_game_state(self, game_name, channel_id):
        cursor = self._connection.cursor()
        cursor.execute("delete from game_states where game_name=%s and channel_id=%s",
                       (game_name, channel_id))

    def get_all_game_states(self, game_name):
        results = []
        cursor = self._connection.cursor()
        cursor.execute("select channel_id, game_state from game_states where game_name=%s", [game_name])
        rows = cursor.fetchall()
        for row in rows:
            results.append({
                "channel_id": row[0],
                "json_game_state": row[1]
            })
        return results

    def load_game_state(self, game_name, channel_id):
        cursor = self._connection.cursor()
        cursor.execute("select game_state from game_states where game_name=%s and channel_id=%s",
                       (game_name, channel_id))

    def save_game_state(self, game_name, channel_id, game_state):
        cursor = self._connection.cursor()
        cursor.execute("insert into game_states (game_name, channel_id, game_state) "
                       "values (%s, %s, %s) "
                       "on conflict on constraint game_states_game_name_channel_id_key "
                       "do update set game_state=%s ",
                       (game_name, channel_id, game_state, game_state))
