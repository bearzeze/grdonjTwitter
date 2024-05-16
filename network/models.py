from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):   
    # Follower doesn't need to be followed so that is why symmetrical is False
    followers = models.ManyToManyField('self', symmetrical=False, related_name="following")
    def __str__(self) -> str:
        return self.username


class Post(models.Model):
    def _get_unknown_user():
        return User.objects.get_or_create(username="Unknown")[0]
    
    user = models.ForeignKey(User, on_delete=models.SET(_get_unknown_user), related_name="posts")
    content = models.TextField(max_length=1000, blank=False)
    date_post = models.DateTimeField(auto_now_add=True, blank=True)
    edited = models.BooleanField(default=False, blank=True)
    date_edit = models.DateTimeField(null=True, blank=True)
    
    # serialize into JSON object
    def serialize(self):
        json = {
                "id": self.id,
                "user": self.user.username,
                "body": self.content,
                "posting_date": self.date_post,
            }
        
        if self.edited:
            json["edit"] = {"edited": True, "editing_date": self.date_edit}
            
        return json
    
    def count_likes(self):
        number_of_likes_per_post = self.like_set.count()
        return number_of_likes_per_post
    
    
    # Ordering by reverse chronicogal dates
    class Meta:
        ordering = ["-date_post"]
    
   
# Model for likes 
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ("user", "post")
    
    
    