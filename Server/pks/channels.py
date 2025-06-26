import logging

from .database import Database


class Channels:
    def __init__(self, bot):
        self.bot = bot
        self.db = ChannelsDatabase()

    def add(self, chat_id: str) -> None:
        if self.db.channel_exists(chat_id):
            self.db.set_active(chat_id)
        else:
            self.db.add(chat_id)

    def disable(self, chat_id: str) -> None:
        if self.db.channel_exists(chat_id):
            self.db.disable(chat_id)

    def broadcast(self, message: str) -> None:
        logging.info(f"Broadcasting message: \"{message}\"")
        for chat_id in self.list_active_channels():
            self.bot.send_message(chat_id, message)

    def list_active_channels(self) -> list:
        column = self.db.query_column(self.db.db_columns[0])
        return [row for row in column if column[row] is True]

    def list_all_channels(self) -> list:
        return [chan for chan in self.db.query_column(self.db.db_columns[0])]


class ChannelsDatabase(Database):
    def __init__(self):
        super().__init__(
            "db/channels.db",
            {
                "channels": dict
            }
        )

    def channel_exists(self, chat_id: str) -> bool:
        return self.key_exists(self.db_columns[0], chat_id)

    def set_active(self, chat_id: str) -> None:
        self.update(self.db_columns[0], chat_id, True)

    def add(self, chat_id: str) -> None:
        self.insert_dict(self.db_columns[0], {chat_id: True})

    def disable(self, chat_id: str) -> None:
        print(f"Disabling channel {chat_id}")
        self.update(self.db_columns[0], chat_id, False)
