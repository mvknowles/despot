#!/usr/bin/env python3

import json
from pathlib import Path

pad = " " * 4
for playlist_path in Path("despotify/playlists").iterdir():
    print("Playlist:", playlist_path)

    with playlist_path.open("r") as fh:

        for item in json.load(fh):
            track = item["track"]

            artists = ",".join([a["name"] for a in track["artists"]])
            print(pad, "Artists:", artists)
            print(pad, "Album name:", track["album"]["name"])
            print(pad, "Track name:", track["name"])
