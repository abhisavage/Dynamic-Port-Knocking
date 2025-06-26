import shelve
import os


class Database:
    def __init__(self, db_name: str, columns: dict):
        
        self.db_name = db_name
        self.db = self.__get_db(self.db_name)
        self.db_columns = list(columns.keys())
        for column in columns:
            if not self.column_exists(column):
                self.db[column] = (columns[column])()
        self.db.sync()

    def __del__(self):
        self.db.close()

    def __get_db(self, db_name: str) -> shelve.DbfilenameShelf:
        
        try:
            os.mkdir("/".join(db_name.split("/")[:-1]))
        except FileExistsError:
            pass
        db = shelve.open(db_name)
        return db

    def insert_new_column(self, column_name: str, column_type: type) -> None:
        
        if column_type == dict:
            ins = {column_name: {}}
        elif column_type == list:
            ins = {column_name: []}
        elif column_type == tuple:
            ins = {column_name: ()}
        else:
            raise TypeError(f"Invalid column type: {column_type} for new column named \"{column_name}\"")
        self.db_columns.append(column_name)
        self.db.update(ins)

    def column_exists(self, column: str) -> bool:
        
        return column in self.db

    def key_exists(self, column: str, key: str) -> bool:
        
        # assert self.column_exists(column)
        # assert type(key) == str
        return key in self.db[column]

    def insert_dict(self, column: str, pair: dict) -> None:
        
        cl = self.db[column]
        # assert type(cl) == dict
        cl.update(pair)
        self.db[column] = cl
        self.db.sync()

    def insert_list(self, column: str, value) -> None:
        cl = self.db[column]
        # assert type(cl) == list
        cl.append(value)
        self.db[column] = cl
        self.db.sync()

    def update(self, column: str, key: str, value) -> None:
        # assert self.column_exists(column)
        # assert self.key_exists(column, key)
        cl = self.db[column]  # Get a copy of the column.
        cl[key] = value  # Alters the copy.
        self.db[column] = cl  # Replace the original by the copy.
        self.db.sync()  # Update the database.

    def query_column(self, search_column: str) -> any:
        # assert self.column_exists(search_column)
        return self.db[search_column]

    def query(self, search_column: str, search_key: str) -> any:
        # assert self.column_exists(search_column)
        # assert self.key_exists(search_column, search_key)
        return self.db[search_column][search_key]
