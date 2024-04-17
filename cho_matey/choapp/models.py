from django.db import models


class BaseModel(models.Model):
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
    
     class Meta:
         abstract = True
         
class Users(BaseModel):
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    
    class Meta:
        db_table = 'users'