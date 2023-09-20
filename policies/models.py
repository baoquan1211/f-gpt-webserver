from django.db import models


class Policy(models.Model):
    name = models.TextField(null=False, default="", blank=True)
    policy = models.TextField(null=False, default="", blank=True)

    class Meta:
        db_table = "chat_policies"
