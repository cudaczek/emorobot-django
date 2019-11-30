from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from rest_framework.response import Response
from rest_framework.views import APIView

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
        question_form = self.form_class(request.POST)
        answer_form = RecognitionConfigForm()
        if question_form.is_valid():
            question_form.save()
            return self.render_to_response(self.get_context_data(sucess=True))
        else:
            return self.render_to_response(
                self.get_context_data(question_form=question_form, answer_form=answer_form)
            )


class SavingFormView(FormView):
    form_class = SavingConfigForm
    template_name = 'control_panel.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        question_form = self.form_class(request.POST)
        file_name = question_form.data["file_name"]
        from django.apps import apps
        data_saver = apps.get_app_config('monitor').data_saver
        if request.POST["button"] == "Start":
            data_saver.start_saving_data(file_name)
        elif request.POST["button"] == "Stop":
            data_saver.stop_saving_data()
        config_form = RecognitionConfigForm(self.request.GET or None)
        saving_form = SavingConfigForm(self.request.GET or None, initial={'file_name': file_name})
        context = self.get_context_data(**kwargs)
        context['config_form'] = config_form
        context['saving_form'] = saving_form
        return render(request, self.template_name, context)


# Data getters #

def get_data(request, *args, **kwargs):
    data = {
        "happy": 100,
        "sad": 80,
    }
    return JsonResponse(data)  # http response


def get_current_data(request, *args, **kwargs):
    from django.apps import apps
    receiver = apps.get_app_config('monitor').receiver
    audio_recognizer = receiver.emotion_data["audio"]
    video_recognizer = receiver.emotion_data["video"]
    video_emotions = get_emotions_without_timestamp(video_recognizer)
    audio_emotions = get_emotions_without_timestamp(audio_recognizer)
    return JsonResponse({"audio_recognizer_labels": list(audio_emotions.keys()),
                         "audio_recognizer_data": list(audio_emotions.values()),
                         "video_recognizer_labels": list(video_emotions.keys()),
                         "video_recognizer_data": list(video_emotions.values()),
                         })  # http response


def get_emotions_without_timestamp(emotion_dict):
    dict_without_timestamp = {}
    for k, v in emotion_dict.items():
        if k != "timestamp":
            dict_without_timestamp[k] = v
    return dict_without_timestamp


def get_preview_data(request, *args, **kwargs):
    from django.apps import apps
    data_saver = apps.get_app_config('monitor').data_saver
    return JsonResponse({
        "audio_recognizer_labels": data_saver.get_video_labels(),
        "video_recognizer_labels": data_saver.get_audio_labels(),
        "video_data": data_saver.get_video_data(),
        "audio_data": data_saver.get_audio_data()
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
