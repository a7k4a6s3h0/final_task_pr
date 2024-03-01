from django.urls import path
from . import views

urlpatterns = [
    path('login', views.admin_login, name='admin_login'),
    path('', views.admin_home, name='admin_home'),
    path('logout', views.admin_logout, name='admin_logout'),
    path('del_bl', views.view_and_block_user, name='view_and_block_user')
]
