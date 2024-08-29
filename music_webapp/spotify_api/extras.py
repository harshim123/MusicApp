from .models import Token
from django.utils import timezone
from datetime import timedelta
from requests import post, get
from .credentials import CLIENT_ID,CLIENT_SECRET,REDIRECT_URI


BASE_URL = 'https://api.spotify.com/v1/'

#1 . check tokens
def check_tokens(session_id):
    tokens = Token.objects.filter(user = session_id)
    if tokens:
        return tokens[0]
    else:
        print(f"No token found for session ID: {session_id}")
        return None
    
#2 .create and update the token model
def create_or_update_tokens(session_id, access_token, refresh_token, expires_in, token_type):
    #if not access_token:
        #raise ValueError('access_token is None')
   

    tokens = check_tokens(session_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])

    else:
        tokens = Token(
            user=session_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            token_type=token_type
        )
        tokens.save()
        
# 3 check authnetication
def is_spotify_authenticated(session_id):
    tokens = check_tokens(session_id)
    
    if tokens:
        if tokens.expires_in <= timezone.now():
            refresh_token_func(session_id)
        return True
    return False

# refresh token function
def refresh_token_func(session_id):
    refresh_token = check_tokens(session_id).refresh_token
    
    response = post('https://accounts.spotify.com/api/token', data ={
        'grant_type' : "refresh_token",
        'refresh_token' : refresh_token,
        'client_id' : CLIENT_ID,
        'clent_secret' : CLIENT_SECRET,
        'redirect_URI' : REDIRECT_URI,
        
            
    }).json()
    
    access_token = response.get('access_token')
    expires_in = response.get('expires_in')
    token_type = response.get('token_type')
    
    create_or_update_tokens(
        session_id=session_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        token_type=token_type
     )
    
def spotify_requests_execution(session_id, endpoint,params=None):
    token = check_tokens(session_id)
    headers = {'Content-Type' : 'application/json', 'Authorization' : 'Bearer ' + token.access_token}
    
    # get data on the song from the spotify API
    response = get(BASE_URL + endpoint, params=params, headers = headers)
    if response:
        print(response)
    else:
        print('No Response!')
    try:
        return response.json()
    except:
        return{'Error' : 'Issue with request'}
    
    

 