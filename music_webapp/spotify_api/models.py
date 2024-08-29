from django.db import models

# Create your models here.
class Token(models.Model):
    user = models.CharField(unique = True, max_length = 50)
    created_at = models.DateTimeField(auto_now_add=True)
    access_token = models.CharField(max_length = 500, null= False)
    refresh_token = models.CharField(max_length = 500, null = True)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)  
    
    def __str__(self):
        return f"{self.user}'s Spotify Token"