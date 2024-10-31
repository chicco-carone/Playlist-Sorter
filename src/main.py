import os
import sys
import logging
from dotenv import load_dotenv
from PlexConnection import PlexConnection
from db_connection import DBConnection

def setup_logging():
    try:
        os.remove("logs.log")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"An error occurred while removing the log file: {e}")
        sys.exit(1)
    try:
        logging.basicConfig(
            filename="logs.log",
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S")
    except Exception as e:
        print(f"An error occurred while creating the logger: {e}")
        sys.exit(1)

def save_playlist_to_db(db_conn, playlist_name, playlist_data):
    db_conn.add_playlist_data(playlist_name, playlist_data)

setup_logging()
load_dotenv()

plex = PlexConnection(username=os.getenv("PLEX_USERNAME", ""), password=os.getenv(
    "PLEX_PASSWORD", ""), server_name=os.getenv("PLEX_SERVER_NAME", ""))

playlist_data = plex.get_playlist_data("Musica Chicco")

with DBConnection() as db_conn:
    save_playlist_to_db(db_conn, "Musica Chicco", playlist_data)
    sorted_playlist = db_conn.sort_playlist("Musica Chicco", "track_name")

logging.debug(f"Sorted playlist: {sorted_playlist}")

plex.create_playlist("Musica Chicco Sorted", sorted_playlist)
