from datetime import datetime
from rest_framework import response, status, viewsets
from .models import Conversation
from .serializers import ConversationSerializer
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser


class ConversationView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_404_NOT_FOUND
            )
        try:
            conversation_serializer = ConversationSerializer(
                Conversation.objects.filter(deleted_at=None, user_id=request._user.id),
                many=True,
            )

            conversations = conversation_serializer.data

            if conversations:
                return response.Response(conversations, status=status.HTTP_200_OK)
            else:
                return response.Response(
                    "Conversation is not found", status=status.HTTP_404_NOT_FOUND
                )
        except:
            return response.Response(
                "Something went wrong", status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, id):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_404_NOT_FOUND
            )

        try:
            conversation_serializer = ConversationSerializer(
                Conversation.objects.get(
                    id=id, deleted_at=None, user_id=request._user.id
                )
            )
            conversation = conversation_serializer.data
            return response.Response(conversation, status=status.HTTP_200_OK)
        except:
            return response.Response(
                "Conversation is not found", status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, id):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_404_NOT_FOUND
            )
        new_name = request.GET.get("name", "")
        if new_name == "":
            return response.Response(
                "New name is not valid", status=status.HTTP_400_BAD_REQUEST
            )

        conversation = Conversation.objects.get(id=id)
        conversation.name = new_name

        conversation_serializer = ConversationSerializer(
            conversation, data=model_to_dict(conversation)
        )

        if conversation_serializer.is_valid() == False:
            print(conversation_serializer.errors)
            return response.Response(
                "New name is not valid", status=status.HTTP_400_BAD_REQUEST
            )
        conversation_serializer.save()
        return response.Response(
            conversation_serializer.data, status=status.HTTP_200_OK
        )

    def delete(self, request, id):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_404_NOT_FOUND
            )

        conversation = Conversation.objects.get(id=id)
        if conversation is None:
            return response.Response(
                "Conversation not found", status=status.HTTP_404_NOT_FOUND
            )
        try:
            conversation.deleted_at = datetime.now()
            conversation.save()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return response.Response(
                str(error),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
