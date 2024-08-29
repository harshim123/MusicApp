from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView,LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth import login, authenticate
from .forms import SignUpForm

#signup
class SignUpView(FormView):
    template_name = 'home/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.email = form.cleaned_data.get('email')
        user.save()
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=user.username, password=raw_password)
        login(self.request, user)
        return super().form_valid(form)
    
#logout
class LogoutInterfaceView(LogoutView):
    template_name ='home/logout.html'
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    

class LoginInterfaceView(LoginView):
    template_name = 'home/login.html'
    
class HomeView(TemplateView):
    template_name = 'home/home.html'