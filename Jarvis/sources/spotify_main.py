#!/usr/bin/env python3

import argparse
from spotify import SpotifyClient
 
if __name__ == "__main__":
    """Main function"""
    
    # Create Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("function", choices=[
        "play", "stop", "next", "previous", "search", "volume",
        "queue", "create_playlist", "add_to_playlist", "change_device"
    ])
    parser.add_argument("--artist", "-a", help="Artist name")
    parser.add_argument("--song", "-s", help="Song name")
    parser.add_argument("--playlist", "-p", help="Playlist name")
    parser.add_argument("--volume", "-v", help="Volume (int)")
    parser.add_argument("--device", "-d", help="Device name")
    args = parser.parse_args()

    # Execute the well function
    if args.function == "play":
        if args.song or args.playlist:
            SpotifyClient.play(_trackName=args.song, _artistName=args.artist, _playlistName=args.playlist)
        else:
            SpotifyClient.change_state_playback()
    elif args.function == "stop":
        SpotifyClient.change_state_playback()
    elif args.function == "next":
        SpotifyClient.next_track()
    elif args.function == "previous":
        SpotifyClient.previous_track()
    elif args.function == "queue":
        track_id = SpotifyClient.search(_track=args.song, _artist=args.artist)["id"]
        SpotifyClient.add_queue(track_id)
    elif args.function == "search":
        if args.playlist:
            SpotifyClient.search_user_playlist(args.playlist)
        else:
            SpotifyClient.search(_track=args.song, _artist=args.artist)
    elif args.function == "volume":
        SpotifyClient.volume(args.volume)
    elif args.function == "create_playlist":
        SpotifyClient.playlist_create(args.playlist)
    elif args.function == "add_to_playlist":
        SpotifyClient.add_track_to_playlist(args.playlist, args.song, args.artist)
    elif args.function == "change_device":
        SpotifyClient.change_device(args.device)
