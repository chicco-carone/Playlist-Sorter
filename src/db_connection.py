import sqlite3
import logging
from typing import List, Tuple, Dict


class DBConnection:
    """
    Class for managing SQLite database connections.
    """

    def __init__(self) -> None:
        logging.getLogger("DBConnection").setLevel(logging.DEBUG)
        logging.error("Database name not provided")
        self.db_name = "PlexSorter.db"
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            logging.info(f"Connected to database '{self.db_name}' successfully")
            self.setup_database()
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            logging.info(f"Connected to database '{self.db_name}' successfully")
            return self
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.conn:
                self.conn.close()
                logging.info("Database connection closed")
        except sqlite3.Error as e:
            logging.error(f"Error closing the database connection: {e}")


    def setup_database(self) -> None:
        """
        Sets up the database by creating tables and populating allowed URL prefixes.

        Args:
            db_name (str): Name of the SQLite database to connect to.
        """
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    track_name TEXT,
                    album_name TEXT,
                    artist_name TEXT,
                    track_id TEXT
                )
            """)
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS application_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    track_name TEXT,
                    album_name TEXT,
                    artist_name TEXT,
                    track_id TEXT
                )
            """)
            
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS plex_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    track_name TEXT,
                    album_name TEXT,
                    artist_name TEXT,
                    track_id TEXT
                    )
                    """)
            
            self.commit()
            logging.info(
                "Database set up successfully: created table 'queue'")
        except sqlite3.Error as e:
            logging.error(f"Error setting up database: {e}")
            raise

    def execute(self, query: str, data: Tuple = ()) -> sqlite3.Cursor:
        """
        Executes an SQL query.

        Args:
            query (str): The SQL query to execute.
            data (Tuple, optional): The data to be passed to the query. Defaults to ().

        Returns:
            sqlite3.Cursor: The cursor object resulting from the query execution.
        """
        try:
            result = self.cursor.execute(query, data)
            logging.info(f"Executed query: {query}")
            return result
        except sqlite3.Error as e:
            logging.error(f"Error executing query '{query}': {e}")
            raise

    def commit(self) -> None:
        """
        Commits the current transaction.
        """
        try:
            self.conn.commit()
            logging.info("Transaction committed successfully")
        except sqlite3.Error as e:
            logging.error(f"Error committing transaction: {e}")
            raise

    def close(self) -> None:
        """
        Closes the connection to the database.
        """
        try:
            self.conn.close()
            logging.info("Database connection closed")
        except sqlite3.Error as e:
            logging.error(f"Error closing the database connection: {e}")
            raise

    def get_playlist_data(self, table_name: str) -> List[Tuple]:
        """
        Gets all the playlists from the server

        Returns:
            List[Tuple]: A list of tuples with the name of the playlist as key and the playlist id as value
        """
        query = f"SELECT * FROM {table_name}"
        result = self.execute(query)
        return result.fetchall()
    
    def add_track_data(self, table_name: str, data: Tuple) -> None:
        """
        Adds a new track into the playlist to the database

        Args:
            table_name (str): The name of the table to add the playlist to
            data (Tuple): The data to add to the table
        """
        query = f"INSERT INTO {table_name} (track_name, album_name, artist_name, track_id) VALUES (?, ?, ?, ?, ?)"
        self.execute(query, data)
        self.commit()
        
        
    def remove_track_data(self, table_name: str, track_id: str) -> None:
        """
        Removes a track from the playlist in the database

        Args:
            table_name (str): The name of the table to remove the track from
            track_id (str): The id of the track to remove
        """
        query = f"DELETE FROM {table_name} WHERE track_id = ?"
        self.execute(query, (track_id,))
        self.commit()
        
    def add_playlist_data(self, table_name: str, data: Dict[str, Dict[str, str]]) -> None:
        """
        Adds a new playlist to the database

        Args:
            table_name (str): The name of the table to add the playlist to
            data (Dict[str, Dict[str, str]]): The data to add to the table
        """
        for track_name, track_data in data.items():
            self.add_track_data(table_name, (track_data["name"], track_name, track_data["album"], track_data["artist"], track_data["ratingKey"]))

    def get_track_data(self, table_name: str = "", track_id: str = "", album_name: str = "", artist_name: str = ""):
        """
        Retrieves track data from the specified table based on the given parameters.

        Args:
            table_name (str, optional): The name of the table to retrieve data from. Defaults to "".
            track_id (str, optional): The ID of the track. Defaults to "".
            album_name (str, optional): The name of the album. Defaults to "".
            artist_name (str, optional): The name of the artist. Defaults to "".

        Returns:
            list: A list of rows containing the track data.
        """
        query = f"SELECT * FROM {table_name} WHERE 1=1"
        params = []
        if track_id:
            query += " AND track_id = ?"
            params.append(track_id)
        if album_name:
            query += " AND album_name = ?"
            params.append(album_name)
        if artist_name:
            query += " AND artist_name = ?"
            params.append(artist_name)
        result = self.execute(query, tuple(params))
        return result.fetchall()
    
    def sort_playlist(self, table_name: str, column: str) -> List[Tuple]:
        """
        Sorts a playlist by song title

        Args:
            table_name (str): The name of the table to sort
            column (str): The column to sort by

        Returns:
            List[Tuple]: A sorted list of tuples with the song title as key and the song rating key as value
        """
        query = f"SELECT * FROM {table_name} ORDER BY {column}"
        result = self.execute(query)
        return result.fetchall()