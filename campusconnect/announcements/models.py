from django.db import models
from accounts.models import User  # custom user model

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()  # ensure field name is exactly 'body'
    created_by_name = models.CharField(max_length=200, blank=True)  # optional user-entered name
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
