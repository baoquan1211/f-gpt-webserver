from rest_framework import response, status, viewsets
from .models import Policy
from .serializers import PolicySerializer
from django.forms.models import model_to_dict


class PolicyView(viewsets.ViewSet):
    def list(self, request):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_404_NOT_FOUND
            )
        try:
            Policy_serializer = PolicySerializer(
                Policy.objects.filter(id__gt=0).order_by("id"), many=True
            )

            Policies = Policy_serializer.data
            if Policies:
                return response.Response(Policies, status=status.HTTP_200_OK)
            else:
                return response.Response(
                    "Services agreement is not found", status=status.HTTP_404_NOT_FOUND
                )
        except:
            return response.Response(
                "Something went wrong", status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, id):
        if request is None:
            return response.Response(
                "Response is not valid", status=status.HTTP_400_BAD_REQUEST
            )
        new_name = request.data.get("name", "")
        new_policy = request.data.get("policy", "")

        if new_name == "":
            return response.Response(
                "New name is not valid", status=status.HTTP_400_BAD_REQUEST
            )
        if new_policy == "":
            return response.Response(
                "New policy is not valid", status=status.HTTP_400_BAD_REQUEST
            )

        policies = Policy.objects.get(id=id)
        policies.name = new_name
        policies.policy = new_policy

        policy_serializer = PolicySerializer(data=model_to_dict(policies))

        if policy_serializer.is_valid() == False:
            return response.Response(
                "New name is not valid", status=status.HTTP_400_BAD_REQUEST
            )
        policies.save()
        return response.Response(policy_serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = PolicySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return response.Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except:
                return response.Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

    def delete(self, request, id):
        if request is None:
            return response.Response(
                "Respose is not valid", status=status.HTTP_404_NOT_FOUND
            )
        policy = Policy.objects.get(id=id)
        if policy is None:
            return response.Response(
                "Policy not found", status=status.HTTP_404_NOT_FOUND
            )
        try:
            policy.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return response.Response(
                str(error),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
