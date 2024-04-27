"""
Nathan Deininger, Makhayla Icard, Sloan Ritter
DSC 200-001 Fall 2023 Data Wrangling
Lab 8
Explanation: This program allow you to choose one of two data sources from a public API. The first
             API is for a PoetryDB that provides data about poems in response to a variety of parameters
             that the user can provide. This poetryDB does not require any authentication. The second public
             API is from Spotify, which does require OAuth authentication. To make interacting with this API
             easier, we have employed the spotipy (requires 'pip install spotipy') library, which provides
             easy interaction with Spotify's API. This API is used to retrieve the top tracks for a specific artist
             Output from the poem and Spotify APIs will be stored in 'poemData.csv', and 'artistData.csv', respectively
"""
# Program imports
import os
import pandas as pd
import requests as req
# Special custom Spotify API library, requires 'pip install spotipy'
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# Set directory to where this Python script is to avoid weird errors
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)


# Accesses the poetryDB public API and stores the response in a CSV file.
# API Information: https://github.com/thundercomb/poetrydb#readme
def datasetOne(title):
    # If user provides a title to search, create URL with title
    if title:
        URL = 'https://poetrydb.org/title/' + title + '/lines.json'

        # Make request to URL
        response = req.get(URL)

        # If API doesn't find anything with given request, inform user and don't write CSV file
        if ('reason' in response.json() and response.json()['reason'] == 'Not found'):
            print("The API was not able to find any poem data with the provided title.")
            return

        # Otherwise, if API gets a response, put that into a CSV file
        print("API successfully retrieved Poem data. Visit 'poemData.csv' to see the output.")

        # Create a dataFrame, write to csv
        df = pd.DataFrame(response.json())
        # Use explode to split the lists into separate rows
        df = df.explode('lines').reset_index(drop=True)
        df.to_csv('poemData.csv', index=False)

    # Otherwise, use default title
    else:
        URL = 'https://poetrydb.org/title/Ozymandias/lines.json'

        # Make request to URL
        response = req.get(URL)

        print("API successfully retrieved poem data for 'Ozymandias' by Shelley. Visit 'poemData.csv' to see the outputs.")

        # Create a dataFrame, write to csv
        df = pd.DataFrame(response.json())
        # Use explode to split the lists into separate rows
        df = df.explode('lines').reset_index(drop=True)
        df.to_csv('poemData.csv', index=False)


# Accesses the Spotify API using spotipy library and stores the response in a CSV file. Requires 'pip install spotipy' to use!
# Client ID: X
# Client Secret:X
# Artist ID: X
def datasetTwo():

    client_id = 'X'
    client_secret = 'X'
    artist_id = 'X'

    # Initialize Spotify client credentials manager
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    # Create a Spotipy instance
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Use spotipy to get artist's top tracks
    top_tracks = sp.artist_top_tracks(artist_id)

    # Parse top tracks response, store it in a df and write to csv
    track_names = []
    artist_names_list = []
    album_names = []

    # Extract data for each track
    for track in top_tracks['tracks']:
        # Extract track name
        track_name = track['name']
        track_names.append(track_name)

        # Extract artist names
        artists_names = []
        for artist_info in track['artists']:
            artists_names.append(' ' + artist_info['name'])
        artist_names_list.append(', '.join(artists_names))

        # Extract album name
        album_name = track['album']['name']
        album_names.append(' ' + album_name)

    df = pd.DataFrame({
        'trackName': track_names,
        ' artist(s)Name': artist_names_list,
        ' albumName': album_names
    })

    df.to_csv('artistData.csv', index=False)
    print("API successfully retrieved artist data. Visit 'artistData.csv' to see the output.")


def menu():
    print("This program allows you to retrieve poem or artist data.")
    choice = input("Enter either '1' or '2' to choose, respectively: ")

    if choice == '1':
        print("You have the option to search for a specific poem by providing part of or all of a poem title.")
        title = input("If you want to try a title, enter it here. Otherwise enter nothing and press enter for the default response: ")
        datasetOne(title)
    elif choice == '2':
        datasetTwo()
    else:
        print("Invalid choice, please come back and try again.")


menu()
