# Starcraft2FantasyPicks

Given a list of player names, rank them by recent performance via the Aligulac API.

This was created to sort a list of players for fantasy draft picks, but you could use it for any sort of player ranking.

## Getting Started
1. Visit http://aligulac.com/about/api/ and generate an API key.
2. Place the API key in a file `api.key`.
3. Place a list of players in `players.txt` with nothing else.
4. Run `rank.py` to generate `rankings.csv`.

## Requirements
These are the versions I had installed at the time of writing; I'm sure the script can run on older versions.
* Python 3.9 or greater
* pandas==1.4.2
