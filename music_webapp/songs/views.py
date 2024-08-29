

# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView
from .models import Song
from django.contrib.auth.mixins import LoginRequiredMixin

class IndexView(LoginRequiredMixin,TemplateView):
    template_name = 'songs/index.html'
    login_url = 'login'

class SongsView(LoginRequiredMixin,ListView):
    model = Song
    template_name = 'songs/songs.html'
    context_object_name = 'songs'
    login_url = 'login'
    
    def get_queryset(self):
        return Song.objects.all()

class SongPostView(LoginRequiredMixin,DetailView):
    model = Song
    template_name = 'songs/songpost.html'
    context_object_name = 'song'
    pk_url_kwarg = 'id'
    login_url = 'login'
