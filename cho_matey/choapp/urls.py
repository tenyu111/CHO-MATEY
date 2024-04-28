from django.urls import path
from .import views
from .views import LogoutConfirmView

urlpatterns = [
    path('', views.start, name='start'),
    path('signup/', views.signup, name='signup'),  
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/confirm/', LogoutConfirmView.as_view(), name='logout_confirm'),
    path('home/', views.home, name='home'),
    path('mypage/', views.mypage, name='mypage'),   
    path('create_post/', views.create_post, name='create_post'), 
    path('post_detail/<int:post_id>', views.post_detail, name='post_detail'),   
     path('delete_reaction/<int:reaction_id>/',views.delete_reaction, name='delete_reaction'),
    path('report_result/<int:post_id>', views.report_result, name='report_result'),
    path('edit_result/<int:post_id>/<int:result_id>/', views.edit_result, name='edit_result'),      
    path('liked_post/', views.liked_post, name='liked_post'),
    path('liked_posts_view/', views.liked_posts_view, name='liked_posts_view'),
    path('edit-delete-post/<int:post_id>/', views.edit_delete_post, name='edit_delete_post'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),   

]
