from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path('signup', views.user_signup, name="user_signup"),
    path('login', views.user_login, name='user_login'),
    path('logout', views.user_logout, name='user_logout'),
    path('send_otp', views.sent_otps, name="send_otp"),
    path('verify_otp', views.verify_otp, name="verify"),
    path('resend_otp', views.verify_otp, name="resend"),
    path('profile', views.profile_page, name='profile_page'),

    path('add_cate', views.add_category, name="add_category"),
    path('add_movie', views.add_movies, name="add_movies"),
    path('edit_movies/<int:id>', views.edit_movies, name="edit_movies"),
    path('added_movie', views.added_movies, name="added_movies"),
    path('delete_movie/<int:id>',views.delete_movies,name="delete_movie"),

    path('search', views.search_movies, name="search_movies"),
    path('add_comment/<int:movie_id>/<int:user_id>', views.add_comment, name="add_comment"),
    path('add_likes/<int:movie_id>/<int:user_id>', views.add_likes, name="add_likes"),
    path('reviews/<int:id>', views.view_movie_reviews, name="reviews"),



]

