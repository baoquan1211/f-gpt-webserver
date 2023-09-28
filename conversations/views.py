from datetime import datetime
from rest_framework import response, status, viewsets
from .models import Conversation
from .serializers import ConversationSerializer
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAuthenticated
from conversations.pdf import PDF
import json
from django.http import HttpResponse


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
            return response.Response(conversations, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            return response.Response(
                "Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list_for_admin(self, request):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_404_NOT_FOUND
            )
        try:
            if request._user.is_staff:
                conversation_serializer = ConversationSerializer(
                    Conversation.objects.filter(),
                    many=True,
                )
                conversations = conversation_serializer.data
                return response.Response(conversations, status=status.HTTP_200_OK)
            else:
                return response.Response(
                    "Just admin can access this link.",
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as error:
            print(error)
            return response.Response(
                "Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
                "Conversation is not found",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_for_admin(self, request, id):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_404_NOT_FOUND
            )

        try:
            if request._user.is_staff:
                conversation_serializer = ConversationSerializer(
                    Conversation.objects.get(id=id)
                )
                conversation = conversation_serializer.data
                return response.Response(conversation, status=status.HTTP_200_OK)
            else:
                return response.Response(
                    "Just admin can access this link.",
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except:
            return response.Response(
                "Conversation is not found",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

    def export_pdf(self, request, id):
        try:
            conversation = Conversation.objects.get(
                id=id, deleted_at=None, user_id=request._user.id
            )

            pdf = PDF()
            pdf_bytes_string = pdf.export(
                conversation=json.loads(conversation.messages),
                username=request._user.name,
            )

            return HttpResponse(
                bytes(pdf_bytes_string),
                content_type="application/pdf",
            )
        except Exception as error:
            return response.Response(
                str(error),
                status=status.HTTP_404_NOT_FOUND,
            )
