from rest_framework import serializers
from .models import WordsFilter, BlockedMessage


class WordsFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordsFilter
        fields = "__all__"


class BlockedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedMessage
        fields = "__all__"
