from django.db import models


# Create your models here.
class WordsFilter(models.Model):
    key_words = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "chat_words_filter"
