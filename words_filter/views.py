from rest_framework import response, status, viewsets
from rest_framework.permissions import IsAdminUser
from words_filter.serializers import BlockedMessageSerializer, BlockedMessage
from words_filter.models import WordsFilter
import json


class BlockedMessageView(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_400_BAD_REQUEST
            )
        try:
            serializer = BlockedMessageSerializer(
                BlockedMessage.objects.all(),
                many=True,
            )

            blocked_messages = serializer.data
            return response.Response(blocked_messages, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            return response.Response(
                "Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, id):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_400_BAD_REQUEST
            )
        try:
            serializer = BlockedMessageSerializer(BlockedMessage.objects.get(id=id))

            blocked_messages = serializer.data
            if blocked_messages:
                return response.Response(blocked_messages, status=status.HTTP_200_OK)
            else:
                return response.Response("Not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            print(error)
            return response.Response(
                "Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


async def message_filter(message, conversation):
    blocked_words = []
    lower_message = message.lower()
    splited_message = lower_message.split()
    list_word_of_message = []
    for word in splited_message:
        word = word.replace(",", "")
        word = word.replace(".", "")
        list_word_of_message.append(word)

    blocked_words = WordsFilter.objects.get()
    if blocked_words is None:
        return blocked_words
    blocked_words = json.loads(blocked_words.key_words)

    founded_words = []
    for word in blocked_words:
        if word in list_word_of_message:
            founded_words.append(word)

    if len(founded_words) > 0:
        try:
            blocked_words = BlockedMessage(
                key_words=json.dumps(founded_words),
                conversation=conversation,
                message=message,
            )
            blocked_words.save()
        except Exception as ex:
            print(ex)
        return True
    return False
