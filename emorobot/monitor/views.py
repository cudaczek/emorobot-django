import datetime

from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.apps import apps

from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import RecognitionConfigForm, SavingConfigForm

User = get_user_model()


def index(request):
    return render(request, "index.html", {"happy": 101})


def preview_stats(request):
    return render(request, "time_stats.html")


def current_stats(request):
    return render(request, "current_stats.html")


# Control Panel #

class ControlPanelView(TemplateView):
    template_name = 'control_panel.html'

    def get(self, request, *args, **kwargs):
        config_form = RecognitionConfigForm(self.request.GET or None)
        saving_form = SavingConfigForm(self.request.GET or None)
        context = self.get_context_data(**kwargs)
        context['config_form'] = config_form
        context['saving_form'] = saving_form
        return self.render_to_response(context)


class ConfigFormView(FormView):
    form_class = RecognitionConfigForm
    template_name = 'control_panel.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        config_sender = apps.get_app_config('monitor').config_sender
        config = {}
        question_form = self.form_class(request.POST)
        if question_form.data['send_updates'] is not None:
            config['update_cycle_on'] = question_form.data['send_updates']=='on' 
        config_sender.send_config(**config)
        config_form = RecognitionConfigForm(self.request.GET or None)
        saving_form = SavingConfigForm(self.request.GET or None)
        context = self.get_context_data(**kwargs)
        context['config_form'] = config_form
        context['saving_form'] = saving_form
        return render(request, self.template_name, context)
        


class SavingFormView(FormView):
    form_class = SavingConfigForm
    template_name = 'sample_forms/index.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        answer_form = self.form_class(request.POST)
        question_form = SavingConfigForm()
        if answer_form.is_valid():
            answer_form.save()
            return self.render_to_response(self.get_context_data(sucess=True))
        else:
            return self.render_to_response(
                self.get_context_data(answer_form=answer_form, question_form=question_form)
            )


# Data getters #

def get_data(request, *args, **kwargs):
    data = {
        "happy": 100,
        "sad": 80,
    }
    return JsonResponse(data)  # http response


def get_current_data(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_recognizer = receiver.emotion_data["audio"]
    video_recognizer = receiver.emotion_data["video"]
    return JsonResponse({"audio_recognizer_labels": list(audio_recognizer.keys()),
                         "audio_recognizer_data": list(audio_recognizer.values()),
                         "video_recognizer_labels": list(video_recognizer.keys()),
                         "video_recognizer_data": list(video_recognizer.values()),
                         })  # http response


def get_preview_data(request, *args, **kwargs):
    audio_recognizer = {
        "female_angry": 1.456557,
        "female_calm": 3.3254342,
        "female_fearful": 12.232114,
        "female_happy": 1.12341e-5,
        "female_sad": -1.7,
        "male_angry": 2.43564,
        "male_calm": 1.234,
        "male_fearful": 3.5464,
        "male_happy": 7.23425,
        "male_sad": 2.1234
    }
    video_recognizer = {
        "angry": 3.1,
        "disgust": 5.777,
        "fear": 2.0001,
        "happy": 0.756,
        "sad": -1.97,
        "suprise": 10.56,
        "neutral": 0.899
    }
    date = "2019-09-29"
    return JsonResponse({"time_stats": [
        {
            "t": datetime.datetime.strptime(date, '%Y-%m-%d'),
            "x": 100
        }
    ],
        "audio_recognizer_labels": list(audio_recognizer.keys()),
        "video_recognizer_labels": list(video_recognizer.keys()),
    })  # http response


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
