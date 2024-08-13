import os
import sys
import logging
from dotenv import load_dotenv
from PlexConnection import PlexConnection


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


setup_logging()
load_dotenv()


plex = PlexConnection(username=os.getenv("PLEX_USERNAME", ""), password=os.getenv(
    "PLEX_PASSWORD", ""), server_name=os.getenv("PLEX_SERVER_NAME", ""))

playlist_data = plex.get_playlist_data("Musica Chicco")

sorted_playlist = plex.sort_playlist(playlist_data)

logging.debug(f"Sorted playlist: {sorted_playlist}")

plex.create_playlist("Musica Chicco Sorted", sorted_playlist)
