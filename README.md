spotify_wrapper
========


Abstract
--------

**spotify_wrapper** is a wrapper for Spotify API built using Python. The script has currently only one purpose, download informations about Liked Songs (a playlist in Spotify). 

Dependencies
--------

To use **spotify_wrapper** you need to install one additional package: `pyperclip`.
With pip you can install it with this command:

    pip install pyperclip

Usage
--------

It's necessary to have a basic credential to use Spotify API, [here you can find information](https://developer.spotify.com/documentation/general/guides/app-settings/) about how to create and APP and obtain a Client ID and a Client Secret. The `PATH` variable inside the code is configured to look for an environment variable called `PY_SPOTIFY` and if it doesn't find it will set the value of this variable to the current directory (using `os.getcwd`). These are two essential things to have in mind in order to use the script. 

After that, to start using **spotify_wrapper** you need to run the script inside Python shell, it only works inside the shell (I'm using IPython):
  
    In [1]: run Spotify.py

Then it's necessary to create a instance of this class:

    In [2]: spt = spotify()

To this object you can apply two class methods: `getLikedSongs()` and `list_songs()`. The class method `getLikedSongs()` will return the JSON response to the request made to the endpoint, as such:

    'href': 'https://api.spotify.com/v1/albums/6P4wMdPtRficqe9zTxm7jL',
     'id': '6P4wMdPtRficqe9zTxm7jL',
     'images': [{'height': 640,
       'url': 'https://i.scdn.co/image/ab67616d0000b273aa94ca8ca49c2ea033764aaa',
       'width': 640},
      {'height': 300,
       'url': 'https://i.scdn.co/image/ab67616d00001e02aa94ca8ca49c2ea033764aaa',
       'width': 300},
      {'height': 64,
       'url': 'https://i.scdn.co/image/ab67616d00004851aa94ca8ca49c2ea033764aaa',
       'width': 64}],
     'name': 'Glow',
     'release_date': '1976-06-15',
     'release_date_precision': 'day',
     'total_tracks': 9,
     'type': 'album',
     'uri': 'spotify:album:6P4wMdPtRficqe9zTxm7jL'},
    'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/3YR92OLKlvkK5oKNekSqXe'},
      'href': 'https://api.spotify.com/v1/artists/3YR92OLKlvkK5oKNekSqXe',
      'id': '3YR92OLKlvkK5oKNekSqXe',
      'name': 'Al Jarreau',
      'type': 'artist',
      'uri': 'spotify:artist:3YR92OLKlvkK5oKNekSqXe'}],
    'available_markets': ['AD',
     'AE',
     'AR',
     'AT',
     ...
     JSON file containing information about the playlist LIKED SONGS stored

This method will also store this information inside a JSON file called 'LikeSongs_saved.json' in the same directory. 

The second class method `list_songs()` can only be executed once the first one has been executed, because it depends on information gathered by it. It will return an enumerated list of artists and tracks, sorted by the most recent added to your Liked Songs playlists. Here is an example of its output:

    1 Stromae: Alors on danse
    2 José James: Just The Way You Are
    3 Aaron Taylor: Blue
    4 Paul McCartney: Ram On - Remastered 2012
    5 Gal Costa: Barato Total
    6 Nina Simone: I Wish I Knew How It Would Feel to Be Free
    ...
    JSON file containing a list of artist and tracks from LIKED SONGS stored
    
This method will also store the output into a JSON file called 'list_LikedSong.json'.

This is it, I hope soon enough I could add more methods to this wrapper.



