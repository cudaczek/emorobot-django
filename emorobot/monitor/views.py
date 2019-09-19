from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response


User = get_user_model()

def index(request):
    return render(request, "index.html", {"happy": 101})


def get_data(request, *args, **kwargs):
    data = {
        "happy": 100,
        "sad": 80,
    }
    return JsonResponse(data)  # http response


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        qs_count = User.objects.all().count()
        labels = ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange']
        data = {
            "labels": labels,
            "defaultData": [qs_count, 6, 7, 8, 12, 1]
        }
        return Response(data)
