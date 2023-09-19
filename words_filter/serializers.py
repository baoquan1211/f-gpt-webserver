from rest_framework import serializers
from .models import WordsFilter


class WordsFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordsFilter
        fields = "__all__"
