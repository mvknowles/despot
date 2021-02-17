#!/usr/bin/env python3

import json
import spotipy
import argparse
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth

DEFAULT_SAVE_DIR = "despotify"

REDIRECT_URI = "http://127.0.0.1"

# how many items in a page Spotify will let us liberate
ITEM_LIMIT = 50

# How many pages we'll fetch before feeling bad:
# NOTE: Spotify does give info about how many records there are. I don't care.
PAGE_FETCH_LIMIT = 100

FUNCTIONS_WITH_OIL = [
        "current_user_top_artists",
        "current_user_saved_tracks",
        "current_user_top_tracks"
]

SCOPES = [
        "playlist-read-private",
        "user-library-read",
        "user-follow-read",
        "user-read-recently-played",
        "user-top-read",
        "user-read-playback-position"
]


def depaginate(fn, **kwargs):
    loot = []

    for page in range(0, PAGE_FETCH_LIMIT):
        print("Request page number:", page)
        morsel = fn(limit=ITEM_LIMIT, offset=ITEM_LIMIT * page, **kwargs)
        item_count = len(morsel["items"])

        if item_count == 0:
            return loot

        loot.extend(morsel["items"])

    print("Too many requsts to Spotify for my comfort")
    print("Returning incomplete data anyway.")

    return loot


def main():

    parser = argparse.ArgumentParser(description="Liberate Spotify data")
    parser.add_argument("--client-id", dest="client_id", required=True)
    parser.add_argument("--client-secret", dest="client_secret", required=True)
    parser.add_argument(
            "--save-dir", dest="save_dir", default=DEFAULT_SAVE_DIR, type=Path)
    args = parser.parse_args()

    args.save_dir.mkdir(exist_ok=False)

    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=args.client_id,
            client_secret=args.client_secret,
            scope=" ".join(SCOPES),
            redirect_uri=REDIRECT_URI))

    playlists_dir = args.save_dir.joinpath("playlists")
    playlists_dir.mkdir(exist_ok=True)

    print("Despot: Liberating your data to:", playlists_dir)

    print("Saving playlists")
    with args.save_dir.joinpath(
            "current_user_playlists.json").open("w") as fh:
        results = depaginate(spotify.current_user_playlists)
        json.dump(results, fh)

    print("Fetching playlist contents")
    for playlist_number, playlist in enumerate(results):
        print("Playlist:", playlist["name"])

        playlist_path = playlists_dir.joinpath(
                "{}.json".format(playlist_number))
        with playlist_path.open("w") as fh:
            results = depaginate(
                    spotify.user_playlist_tracks, playlist_id=playlist["id"])
            json.dump(results, fh)

    for api_fn in FUNCTIONS_WITH_OIL:
        print("Liberating API:", api_fn)

        with args.save_dir.joinpath(
                "{}.json".format(api_fn)).open("w") as fh:
            results = depaginate(getattr(spotify, api_fn))
            json.dump(results, fh)


if __name__ == "__main__":
    main()
