from django.db import models
from conversations.models import Conversation


# Create your models here.
class WordsFilter(models.Model):
    key_words = models.CharField(blank=True, null=True)

    class Meta:
        db_table = "chat_words_filter"


class BlockedMessage(models.Model):
    message = models.TextField(blank=True, null=True)
    key_words = models.TextField(blank=True, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "chat_blocked_messages"
