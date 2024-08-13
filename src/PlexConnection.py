from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
import logging
import os
from typing import Dict


class PlexConnection:
    def __init__(self, api_key: str = "", username: str = "", password: str = "", server_name: str = "") -> None:
        self.api_key = api_key
        self.username = username
        self.password = password
        self.server_name = server_name
        self.server: PlexServer = None

        if self.api_key != "":
            self._connect_with_token()
        elif (self.username and self.password) != "":
            self._connect_with_credentials()
        else:
            raise ValueError(
                "You must provide either a token or a username and password.")

        if self.server_name == "":
            raise ValueError("You must provide a server name.")

        logging.getLogger().setLevel(logging.DEBUG)

    def _connect_with_token(self) -> None:
        """
        Connects to the server using a token. 
        Gets called by the constructor if there is an api key
        """
        self.server = PlexServer(token=self.api_key)

    def _connect_with_credentials(self) -> None:
        """
        Connect to plex using user credentials.
        Gets called by the constructor if there isn't an api key
        """
        account = MyPlexAccount(username=self.username, password=self.password)
        self.server = account.resource(self.server_name).connect()

    def set_server_name(self, server_name: str) -> None:
        """
        Sets a server name after the connection is established

        Args:
            server_name (str): The name of the plex server to connect
        """
        self.server_name = server_name

    def get_playlists(self) -> Dict[str, str]:
        """
        Gets all the playlists from the server

        Returns:
            Dict[str, str]: A dictionary with the name of the playlist as key and the playlist id as value
        """
        playlists = self.server.playlists()
        return {playlist.title: playlist.key for playlist in playlists}

    def remove_parentesis(self, title: str) -> str:
        """
        Removes all parentheses from a string

        Args:
            title (str): The string to remove parentheses from

        Returns:
            str: The string without parentheses
        """
        new_title = title.replace("(", "").replace(")", "")
        logging.debug(f"New title: {new_title}")
        return new_title

    def get_playlist_data(self, playlist_title: str) -> Dict[str, str]:
        """
        Gets the songs and their info for a given playlist

        Args:
            playlist_title (str): The title of the playlist

        Returns:
            Dict[str, str]: A dictionary with the song title as key and the song rating key as value
        """
        playlist = self.server.playlist(playlist_title)
        songs = playlist.items()
        playlist_data = {}
        for song in songs:
            if song.title.startswith("("):
                title = self.remove_parentesis(song.title)
            else:
                title = song.title
            playlist_data[title] = song.ratingKey
        return playlist_data
            

    def sort_playlist(self, playlist_dict: dict[str, str]) -> dict[str, str]:
        """
        Sorts a playlist by song title

        Args:
            playlist_dict (dict[str, str]): A dictionary with the song title as key and the song rating key as value

        Returns:
            dict[str, str]: A sorted dictionary with the song title as key and the song rating key as value
        """
        return {title: rating_key for title, rating_key in sorted(playlist_dict.items())}
        

    def create_playlist(self, playlist_title: str, songs: Dict[str, str]) -> None:
        """
        Creates a playlist with the given songs

        Args:
            playlist_title (str): The title of the playlist
            songs (Dict[str, str]): A dictionary with the song title as key and the song rating key as value
        """
        logging.debug(f"Creating playlist: {playlist_title}")
        logging.debug(f"Playlist songs: {songs}")
        if songs:
            rating_keys = list(str(songs.values()))
            self.server.createPlaylist(playlist_title, rating_keys)
        else:
            logging.debug("No songs to add to the playlist")
            raise ValueError("Must include items to add when creating new playlist.")

