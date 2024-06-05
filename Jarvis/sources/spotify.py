from spotipy import Spotify,SpotifyOAuth
from spotipy.exceptions import SpotifyException
from dotenv import load_dotenv; load_dotenv()
import webbrowser, time, os

class Device():
    def __init__(self, client:Spotify=None) -> None:
        try:
            self._SpotifyClient = client
            self._openDevices = client.devices()["devices"]
            self._activeDevice = None
        except:
            print("Please define a Spotipy client")
            exit()
        finally:
            self.search_active_device()
    
    def search_active_device(self):
        for device in self._openDevices:
            if device["is_active"]:
                self._activeDevice = device
                break
            elif device == self._openDevices[-1]:
                self._activeDevice = None 
        
    def start_device(self):
        print(self._activeDevice)
        if not self._activeDevice:
            webbrowser.open(url="https://open.spotify.com/")
            time.sleep(5)
            old_devices = self._openDevices
            self._openDevices = self._SpotifyClient.devices()["devices"]
            for device in self._openDevices :
                if not device in old_devices:
                    self._activeDevice = device
                    self._activeDevice["name"] = "JARVIS"
                    
            print(self._activeDevice)

    def change_device(self, device_name) -> int:
        for device in self._openDevices:
            if device_name in device:
                self._activeDevice = device
                self._SpotifyClient.transfer_playback(device_id=device_name["id"], force_play=True)
                return 0
        return 1
    
    def volume(self, volume:float):
        try :
            assert 0 <= volume <= 100
            self._SpotifyClient.volume(volume, self._activeDevice["id"])
            return 0
        except AssertionError:
            return 0
        

class Track():
    def __init__(self, spotify_client:Spotify) -> None:
        self._SpotifyClient = spotify_client 
    
    def search(self, _track:str, _artist:str=None):
        try:
            _query = f"{_track} artist:{_artist}" if _artist else _track
            _result = self._SpotifyClient.search(_query, type="track", limit=1)
            return _result['tracks']['items'][0] if _result else None 
        except SpotifyException:
            return None
    
    def artist(self, _artist:str):
        try:
            _result = self._SpotifyClient(f"artist:{_artist}", type="artist")
            if _result["artists"]["items"]:
                if len(_result['artists']['items']) == 1:
                    return _result['artists']['items'][0]
                else:
                    for artist_found in _result['artists']['items']:
                        if artist_found == _artist:
                            return artist_found
                return None
        except SpotifyException:
            return None

    def artist_top10(self, _artist):
        _artistID = self.artist(_artist)["id"]
        _top10 = self._SpotifyClient.artist_top_tracks(_artistID)
        return _top10["track"][:10]
    
    def add_queue(self, _trackID):
        self._SpotifyClient.add_to_queue(_trackID)
        
class Playlist():
    def __init__(self, spotify_client:Spotify, user=None) -> None:
        self._SpotifyClient = spotify_client
        self._user = user

    def search_playlist(self, _playlist:str):
        _results = self._SpotifyClient.search(q=_playlist, type="playlist", limit=1)
        return _results['tracks']['items'][0] if _results['tracks']['items'] else None
    
    def search_user_playlist(self, _playlist:str):
        _userPlaylists = self._SpotifyClient.current_user_playlists()
        if _userPlaylists:
            for playlist in _userPlaylists:
                if playlist["name"] == _playlist:
                    return playlist
            return None
    
    def playlist_create(self, _playlistName:str)->bool:
        try:
            assert self._user
            if not self.search_user_playlist(_playlistName):
                self._SpotifyClient.user_playlist_create(user=self._user, name=_playlistName, description="", public=False)
        except AssertionError:
            return False
    
    def playlist_delete(self, _playlistName:str)->bool:
        try:
            assert self._user
            _playlist = self.search_user_playlist(_playlistName)
            if _playlist:
                self._SpotifyClient.current_user_unfollow_playlist(_playlist["id"])
            return True
        except AssertionError:
            return False
        
    def playlist_rename(self, _playlistName:str, _playlistNewName:str)->bool:
        try:
            assert self._user
            _playlist = self.search_user_playlist(_playlistName)
            if _playlist:
                self._SpotifyClient.user_playlist_change_details(user=self._user,playlist_id=_playlist["id"], name=_playlistNewName)
                return True
            return False
        except AssertionError:
            return False 

class Playback(Device):
    def __init__(self, client:Spotify = None) -> None:
        super().__init__(client)
    
    def change_state_playback(self):
        if self._SpotifyClient.current_playback()["is_playing"]:
            self._SpotifyClient.pause_playback(self._activeDevice["id"])
        else:
            self._SpotifyClient.start_playback(self._activeDevice["id"])
    
    def next_track(self):
        self._SpotifyClient.next(self._activeDevice["id"])
    
    def previous_track(self):
        self._SpotifyClient.previous(self._activeDevice["id"])

class SpotifyManager(Track, Playlist, Playback):
    def __init__(self, scope:str=None, user:str=None) -> None:
        self._scope = scope
        self._SpotifyClient = Spotify(auth_manager=SpotifyOAuth(scope=self._scope))
        self._user = user
        super().__init__(self._SpotifyClient)
        
    def add_track_to_playlist(self, _playlistName:str,_trackName:str, _artsitName:str=None):
        _userPlaylists = self.search_user_playlist(_playlistName)
        if not _userPlaylists:
            self.playlist_create(_playlistName)
            _playlistID = self.search_user_playlist(_playlistName)["id0"]
        else:
            _playlistID = _userPlaylists["id"]
        
        _trackID = self.search(_trackName)
        if _trackID:
            self._SpotifyClient.playlist_add_items(_playlistID,[_trackID])
            
    def play(self, _trackName=None, _artistName=None, _playlistName=None, _deviceID=None):
        if _trackName:
            _trackURI = self.search(_trackName, _artistName)["uri"]
            self._SpotifyClient.start_playback(device_id=_deviceID, couris=[_trackURI])
        elif _playlistName:
            _playlist = self.search_user_playlist(_playlistName)
            if not _playlist:
                _playlist = self.search_playlist(_playlistName)
            if _playlist:
                self._SpotifyClient.start_playback(device_id=_deviceID, context_uri=_playlist["uri"])
    
    
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-playback-position user-top-read user-read-recently-played"
SpotifyClient = SpotifyManager(scope=SCOPE, user=os.getenv("SPOTIFY_USER"))