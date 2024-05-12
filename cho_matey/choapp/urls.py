from django.urls import path
from .import views
from .views import LogoutConfirmView

urlpatterns = [
    path('', views.introduction, name='intruduction'),
    path('cho-matey/start', views.start, name='start'),
    path('cho-matey/signup/', views.signup, name='signup'),  
    path('cho-matey/login/', views.CustomLoginView.as_view(), name='login'),
    path('cho-matey/logout/confirm/', LogoutConfirmView.as_view(), name='logout_confirm'),
    path('cho-matey/home/', views.home, name='home'),
    path('cho-matey/mypage/', views.mypage, name='mypage'),   
    path('cho-matey/create_post/', views.create_post, name='create_post'), 
    path('cho-matey/post_detail/<int:post_id>', views.post_detail, name='post_detail'),   
    path('cho-matey/delete_reaction/<int:reaction_id>/',views.delete_reaction, name='delete_reaction'),
    path('cho-matey/report_result/<int:post_id>', views.report_result, name='report_result'),
    path('cho-matey/edit_result/<int:post_id>/<int:result_id>/', views.edit_result, name='edit_result'),      
    path('cho-matey/liked_post/', views.liked_post, name='liked_post'),
    path('cho-matey/liked_posts_view/', views.liked_posts_view, name='liked_posts_view'),
    path('cho-matey/edit-delete-post/<int:post_id>/', views.edit_delete_post, name='edit_delete_post'),
    path('cho-matey/edit_profile/', views.edit_profile, name='edit_profile'),   
]
