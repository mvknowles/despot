#!/usr/bin/env python3

import json
import spotipy
import argparse
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth

parser = argparse.ArgumentParser(description="Liberate Spotify data")
parser.add_argument("--client-id", dest="client_id", required=True)
parser.add_argument("--client-secret", dest="client_secret", required=True)
args = parser.parse_args()

REDIRECT_URI = "http://127.0.0.1"

# how many items in a page Spotify will let us liberate
ITEM_LIMIT = 50

# How many pages we'll fetch before feeling bad:
# NOTE: Spotify does give info about how many records there are. I don't care.
PAGE_FETCH_LIMIT = 100

DEFAULT_SAVE_DIR = Path("despotify")

FUNCTIONS_WITH_OIL = [
        "current_user_top_artists",
        "current_user_saved_tracks",
        "current_user_top_tracks"
]

DEFAULT_SAVE_DIR.mkdir(exist_ok=False)

SCOPES = [
        "playlist-read-private",
        "user-library-read",
        "user-follow-read",
        "user-read-recently-played",
        "user-top-read",
        "user-read-playback-position"
]

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=args.client_id,
        client_secret=args.client_secret,
        scope=" ".join(SCOPES),
        redirect_uri=REDIRECT_URI))


def depaginate(fn, **kwargs):
    untarded = []

    for page in range(0, PAGE_FETCH_LIMIT):
        print("Request page number:", page)
        morsel = fn(limit=ITEM_LIMIT, offset=ITEM_LIMIT * page, **kwargs)
        item_count = len(morsel["items"])

        if item_count == 0:
            return untarded

        untarded.extend(morsel["items"])

    raise Exception("I think we just hammered spotify. They'll never recover.")


playlists_dir = DEFAULT_SAVE_DIR.joinpath("playlists")
playlists_dir.mkdir(exist_ok=True)

print("Despot: Liberating your data to:", playlists_dir)

print("Saving playlists")
with DEFAULT_SAVE_DIR.joinpath("current_user_playlists.json").open("w") as fh:
    results = depaginate(spotify.current_user_playlists)
    json.dump(results, fh)

print("Fetching playlist contents")
for playlist in results:
    print("Playlist:", playlist["name"])

    playlist_path = playlists_dir.joinpath("{}.json".format(playlist["id"]))
    with playlist_path.open("w") as fh:
        results = depaginate(
                spotify.user_playlist_tracks, playlist_id=playlist["id"])
        json.dump(results, fh)

for api_fn in FUNCTIONS_WITH_OIL:
    print("Liberating API:", api_fn)

    with DEFAULT_SAVE_DIR.joinpath("{}.json".format(api_fn)).open("w") as fh:
        results = depaginate(getattr(spotify, api_fn))
        json.dump(results, fh)
