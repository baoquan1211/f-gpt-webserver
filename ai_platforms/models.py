from django.db import models

# Create your models here.


class AIPlatform(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    key = models.CharField(null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = "chat_ai_platforms"
