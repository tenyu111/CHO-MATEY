from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class BaseModel(models.Model):
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
    
     class Meta:
         abstract = True


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('ユーザー名は必須です')

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

    
class Users(AbstractBaseUser, BaseModel):
    username = models.CharField(max_length=64,unique=True)
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.username
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True

    is_admin = models.BooleanField(default=False)
    
    @property
    def is_staff(self):
        return self.is_admin
    
    class Meta:
        db_table = 'users'
    

class Product_Categories(models.Model):
    category_name = models.CharField(max_length=16, null=True) 
    def __str__(self):
        return self.category_name
    
    class Meta:
        db_table = 'product_categories'
        
        
class Products(BaseModel):
    category = models.ForeignKey(Product_Categories, on_delete=models.CASCADE) 
    product_name = models.CharField(max_length=256)
    jan_code = models.CharField(max_length=13, null=True)
    asin_code= models.CharField(max_length=10, null=True)
    
    class Meta:
        db_table = 'products'
        
        
class Posts(BaseModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)         
    product = models.ForeignKey(Products, on_delete=models.CASCADE)    
    purchase_place = models.CharField(max_length=200)                 
    price = models.IntegerField(null=True,blank=True)
    image =  models.ImageField(upload_to='images/',default='')                      
    purchase_reason = models.TextField()                              
    
    class Meta:
        db_table = 'posts'
           
                                 
class Liked_Posts(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)          
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)         
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'liked_posts'
        
        
class Reactions(BaseModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)          
    post = models.ForeignKey(Posts, on_delete=models.CASCADE,related_name = 'reactions')         
    comment = models.TextField()
    boost_score = models.IntegerField(
         validators=[MinValueValidator(1), MaxValueValidator(100)],
         blank = True,
         null = True,
    )
    def __str__(self):
        return self.comment
    
    class Meta:
        db_table = 'reactions'
  
        
class Results(BaseModel):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    purchased_product_name = models.CharField(max_length=256, blank=True, null=True) 
    result_category = models.IntegerField(
       choices = [
        (0,'買った'),
        (1,'別の商品を買った'),
        (2,'買わなかった'),
        ]    
    )
    result_image =  models.ImageField(upload_to='result_images/',blank=True)                      
    result_comment = models.TextField(null=True, blank=True) 
    
    class Meta:
        db_table = 'results'