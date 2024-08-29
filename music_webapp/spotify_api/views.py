from django.shortcuts import render

# Create your views here.
# spotify_api/views.py
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from requests import Request, post
from spotipy import Spotify

from spotify_api import credentials
from .credentials import CLIENT_ID, REDIRECT_URI, CLIENT_SECRET
from .extras import *
from django.shortcuts import render
from django.urls import reverse
import requests
from .models import Token
from django.conf import settings
import datetime
import spotipy
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
import time


from django.views import View



'''class AuthenticationURL(APIView):
    def get(self, request, format = None):
        scopes = 'user-read-currently-playing user-modify-playback-state'
        redirect_URI = settings.SPOTIFY_REDIRECT_URI
        client_ID = settings.SPOTIFY_CLIENT_ID
        url = Request('GET', 'https://accounts.spotify.com/authorize', params = {
            'scope' : scopes,
            'response_type': 'code',
            'redirect_uri' : redirect_URI,
            'client_id' :  client_ID,
        }).prepare().url
        return HttpResponseRedirect(url)'''
    
#change if needed
'''def spotify_redirect(request,format = None):
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        return error
    
    response = post('https://accounts.spotify.com/api/token', data ={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,   
    }).json()
    
    access_token = response.get('access_token')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    token_type = response.get('token_type')
    
    authkey = request.session.session_key
    if not request.session.exists(authkey):
        request.session.create()
        authkey = request.session.session_key
        
    create_or_update_tokens(
        session_id=authkey,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        token_type=token_type
    )
    
     # Determine the redirect target based on the query parameter
    redirect_to = request.GET.get('redirect_to', 'current-song')  # Default to 'current-song'
    
    if redirect_to == 'search':
        redirect_url = f"http://127.0.0.1:8000/spotify_api/callback/search?key={authkey}"
    else:
        redirect_url = f"http://127.0.0.1:8000/spotify_api/callback/current-song?key={authkey}"
    
    return HttpResponseRedirect(redirect_url)

# checking whether the user has been authenticated by spotify
class CheckAuthentication(APIView):
    kwarg = "redirect_to"
    def get(self, request, format = None):
        key = self.request.session.session_key
        if not self.request.session.exists(key):
            self.request.session.create()
            key = self.request.session.session_key
            
        #auth_status = is_spotify_authenticated(key)
        
        #redirect_to = request.GET.get(self.kwarg)  # Default to 'current-song'

        
        #if auth_status:
            # Redirect to the appropriate endpoint based on the use case
           # if redirect_to == 'search':
                ##else:
               ##return HttpResponseRedirect(redirect_uri)
        #else:
            # Redirect to authentication URL
            #redirect_uri = "http://127.0.0.1:8000/spotify_api/callback/auth-url"
            #return HttpResponseRedirect(redirect_uri)
    
        
class CurrentSong(APIView):
    kwarg = "key"
    def get(self, request, format=None):
        key = request.GET.get(self.kwarg)
        token = Token.objects.filter(user=key)
        print(token)
        if not is_spotify_authenticated(key):
            # Redirect to authentication if the user is not authenticated
            return HttpResponseRedirect(f"http://127.0.0.1:8000/check-auth?redirect_to=currentSong")
       

        # create an endpoint
        endpoint = "me/player/currently-playing"
        response = spotify_requests_execution(key, endpoint)

        if "error" in response or "item" not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        item = response.get('item')
        progress = response.get('progress_ms')
        is_playing = response.get("is_playing")
        duration = item.get('duration_ms')
        song_id = item.get('id')
        title = item.get("name")
        album_cover = item.get("album").get("images")[0].get("url")

        artists = ""
        for i, artist in enumerate(item.get("artists")):
            if i > 0:
                artists += ", "
            name = artist.get("name")
            artists += name

        song = {
            "id": song_id,
            "title": title,
            "artist": artists,
            "duration": duration,
            "time": progress,
            "album_cover": album_cover,
            "is_playing": is_playing
        }
        print(song)
        return Response(response, status=status.HTTP_200_OK)
    

 # spotify_api/views.py
class SearchSong(APIView):
    kwarg = "key"
    def get(self, request, format=None):
        key = request.GET.get(self.kwarg)
        token = Token.objects.filter(user=key)
        print(token)
        if not is_spotify_authenticated(key):
            # Redirect to authentication if the user is not authenticated
            return HttpResponseRedirect(f"http://127.0.0.1:8000/check-auth?redirect_to=search")

        # Proceed with search if authenticated
        query = request.GET.get("query")
        

        # Create an endpoint
        endpoint = "search"
        params = {"q": query, "type": "track"}
        response = spotify_requests_execution(key, endpoint, params=params)

        if "error" in response or "tracks" not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        tracks = response.get("tracks").get("items")
        search_results = []

        for track in tracks:
            song_id = track.get("id")
            title = track.get("name")
            artists = ""
            for i, artist in enumerate(track.get("artists")):
                if i > 0:
                    artists += ", "
                name = artist.get("name")
                artists += name
            album_cover = track.get("album").get("images")[0].get("url")

            song = {
                "id": song_id,
                "title": title,
                "artist": artists,
                "album_cover": album_cover,
            }
            search_results.append(song)
            print(search_results)
            
            if not request.accepted_renderer.format == 'api':
                return render(request, 'search_results.html', {'search_results': search_results})

        return Response(search_results, status=status.HTTP_200_OK)'''
        
class PlayAlbumView(LoginRequiredMixin, View):
    template_name = 'spotify_api/play_album.html'
    login_url = 'login'
    
    def get(self, request, *args, **kwargs):
        # Logic to retrieve album data if needed
        context = {
            'album_name': 'Album Name',
            'tracks': []  # Replace with actual track data
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=" user-library-read user-modify-playback-state user-read-playback-state user-read-currently-playing "
        ))

        album_uri = request.POST.get('album_uri')

        # Start playback of the album
        try:
            sp.start_playback(context_uri=album_uri)
        except spotipy.SpotifyException as e:
            print(f"Spotify playback error: {e}")
            # Handle the error accordingly, e.g., show an error message to the user

        return redirect('play_album')
 
        
        
class SpotifySearchView(LoginRequiredMixin, ListView):
    template_name = 'spotify_api/search_results.html'
    context_object_name = 'results'
    login_url = 'login'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return []

        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="user-library-read "
        ))

        # Search in Spotify
        results = sp.search(q=query, type='track,album,artist,playlist')
        return results['tracks']['items'] + results['albums']['items'] + results['artists']['items'] + results['playlists']['items']

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        return super().get(request, *args, **kwargs)
 
'''class AddToPlaylistView(View):
    def post(self, request):
        playlist_id = request.POST.get('playlist_id')
        track_uri = request.POST.get('track_uri')
        
        if not playlist_id or not track_uri:
            return HttpResponseBadRequest("Playlist ID and Track URI are required.")
        
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="playlist-modify-public playlist-modify-private user-library-read"
        ))

        try:
            sp.playlist_add_items(playlist_id, [track_uri])
            return JsonResponse({'status': 'success', 'message': 'Track added to playlist'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})'''
        
'''class CreatePlaylistView(LoginRequiredMixin, View):
    template_name = 'spotify_api/create_playlist.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        sp = get_spotify_instance(request)
        user_id = sp.me()['id']

        # Get the playlist name from the form
        playlist_name = request.POST.get('playlist_name')
        public = request.POST.get('public') == 'on'  # Checkbox input for public/private

        # Create the playlist
        sp.user_playlist_create(user=user_id, name=playlist_name, public=public)

        return redirect(reverse('saved_albums'))'''

       
def get_spotify_instance(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read user-modify-playback-state user-read-playback-state user-read-currently-playing "
    )
    
    # Get token info from the session
    token_info = {
        'access_token': request.session.get('spotify_token'),
        'refresh_token': request.session.get('spotify_refresh_token'),
        'expires_at': request.session.get('spotify_token_expiry')
    }

    # Check if the token needs refreshing
    if token_info['expires_at'] and int(token_info['expires_at']) < time.time():
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        request.session['spotify_token'] = token_info['access_token']
        request.session['spotify_token_expiry'] = token_info['expires_at']

    return Spotify(auth=token_info['access_token'])

class LikedSongsView(LoginRequiredMixin, ListView):
    template_name = 'spotify_api/liked_songs.html'
    context_object_name = 'songs'
    login_url = 'login'

    def get_queryset(self):
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="user-library-read "
        ))

        # Fetch liked songs (saved tracks)
        results = sp.current_user_saved_tracks()
        songs = results['items']  # Adjust as needed based on how you want to structure your template

        return songs

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        return super().get(request, *args, **kwargs)

class SavedAlbumsView(LoginRequiredMixin, ListView):
    template_name = 'spotify_api/saved_albums.html'
    context_object_name = 'albums'
    login_url = 'login'

    def get_queryset(self):
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="user-library-read user-modify-playback-state user-read-playback-state user-read-currently-playing"
        ))

        # Fetch saved albums
        results = sp.current_user_saved_albums()
        albums = results['items']  # Adjust as needed based on how you want to structure your template

        return albums

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        return super().get(request, *args, **kwargs)
    
def spotipy_callback(request):
    sp = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-library-read user-modify-playback-state user-read-playback-state user-read-currently-playing"
    )
    token_info = sp.get_access_token(request.GET.get('code'))
    request.session['spotify_token'] = token_info['access_token']
    request.session['spotify_refresh_token'] = token_info['refresh_token']
    request.session['spotify_token_expiry'] = token_info['expires_at']

    return redirect('play_album')

