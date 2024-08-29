# spotify_api/urls.py
from django.urls import path
from . import views
from .views import SavedAlbumsView, LikedSongsView, SpotifySearchView, PlayAlbumView
urlpatterns = [
    
    path('saved-albums/', SavedAlbumsView.as_view(), name='saved_albums'),
    path('spotify_api/callback/', views.spotipy_callback, name='spotipy_callback'),
    path('liked-songs/', LikedSongsView.as_view(), name='liked_songs'),
    path('search/', SpotifySearchView.as_view(), name='spotify_search'),
    #path('add-to-playlist/', AddToPlaylistView.as_view(), name='add_to_playlist'),
    #path('create-playlist/', CreatePlaylistView.as_view(), name='create_playlist'),
    path('play-album/', PlayAlbumView.as_view(), name='play_album'),
]

    
