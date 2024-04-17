from django.urls import path
from .import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.start, name='start'),
    path('signup/', views.signup, name='signup'),  # 'signup/' URLにsignupビューを割り当てる
    path('login/', CustomLoginView.as_view(), name='login'),
]
