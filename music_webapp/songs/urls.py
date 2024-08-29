from django.urls import path
from .views import IndexView, SongsView, SongPostView

urlpatterns = [
    path('index/', IndexView.as_view(), name='index'),
    path('songs/', SongsView.as_view(), name='songs'),
    path('songs/<int:id>/', SongPostView.as_view(), name='songpost'),
]
