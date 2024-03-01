from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class OTP_COLLECTION_db(models.Model):

  email = models.EmailField()
  username = models.CharField(max_length=100)
  otp = models.IntegerField()
  expireTime = models.DateTimeField(blank=False)
  No_of_times = models.IntegerField(default=0)

  class Meta:
    verbose_name="OTP Collection"
    # verbose_name_plural="OTP Collections"

  def __str__(self):
      return f'{self.email} - {self.username}'

class MovieCategory(models.Model):
    category_name = models.CharField(max_length = 50, unique = True)
    describtion = models.TextField(max_length = 1000, null=True, blank=True)
    created = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name="Movie Category"
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"obj - {self.category_name}"      

class Movies(models.Model):
   user = models.ForeignKey(User,on_delete=models.CASCADE)
   movie_title = models.CharField(max_length=50)
   describtion = models.TextField(max_length = 1000)
   image = models.ImageField(upload_to='images/')
   release_date = models.DateTimeField(blank=False)
   actors = models.JSONField(null=True)
   youtube_link = models.CharField(max_length=200)
   category_name = models.ForeignKey(MovieCategory,on_delete=models.CASCADE)
   created_at1 = models.DateTimeField(auto_now_add = True)

   class Meta:
        verbose_name="Movies"
        ordering = ["-created_at1"]
   def __str__(self) -> str:
        return f"obj - {self.movie_title}"  
   
class MovieComment(models.Model):
   movie = models.ForeignKey(Movies,on_delete=models.CASCADE, related_name="reverse_movie")
   user_name = models.ForeignKey(User,on_delete=models.CASCADE, related_name="reverse_user")
   text = models.CharField(max_length=100, null=True)
   likers = models.ManyToManyField(User, related_name="BlogPostLikers", blank=True, null=True)
   created_at2 = models.DateTimeField(auto_now_add = True)


   class Meta:
        verbose_name="Movie Comments"
        ordering = ["-created_at2"]
   
   def __str__(self) -> str:
        return f"obj - {self.movie.movie_title}"  