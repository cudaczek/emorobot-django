import datetime
import os
import struct

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import TemplateView, FormView

from rest_framework.views import APIView
from rest_framework.response import Response

from .msq_receiver import MessageReceiver
from .forms import RecognitionConfigForm, SavingConfigForm
from .nn_evaluator import NeuralNetEvaluator

User = get_user_model()


def index(request):
    return render(request, "index.html")


def preview_stats(request):
    return render(request, "time_stats.html")


def current_stats(request):
    return render(request, "current_stats.html")


def neural_network_evaluator(request):
    filename = None
    context: dict = {}
    try:
        if request.method == 'POST' and request.FILES['uploaded_file']:
            file = request.FILES['uploaded_file']
            if isinstance(file.name, str):
                filename = default_storage.save(file.name, file)

                ext = os.path.splitext(file.name)[1]
                if ext == '.h5':
                    neural_net = NeuralNetEvaluator(file_name=file.name)
                    print("neural net loaded")
                else:
                    return render(request, "nn_evaluator.html",
                                  {'error': "Error: Extension not supported"})
    except MultiValueDictKeyError:
        context = {'error': "Error: You didn't select a file"}
    except UnicodeDecodeError:
        context = {'error': "Error: File contains weird symbols"}
    finally:
        if filename:
            default_storage.delete(filename)
    return render(request, "nn_evaluator.html")


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


def get_current_data(request, *args, **kwargs):
    from django.apps import apps
    # receiver = apps.get_app_config('monitor').receiver
    raw_receiver: MessageReceiver = apps.get_app_config('monitor').receiver_raw
    message = raw_receiver.message
    received_data = struct.unpack('>' + ('h' * (int(len(message) / 2))), message)
    label = "l"
    audio_buffer = []
    for x in received_data:
        audio_buffer.append(x)
        label = x
    print(audio_buffer)
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
        "male_sad": 2.1234,
        label: 1.0
    }
    video_recognizer = {
        "angry": 3.1,
        "disgust": 5.777,
        "fear": 2.0001,
        "happy": 0.756,
        "sad": -1.97,
        "surprise": 10.56,
        "neutral": 0.899
    }
    sample_rate = 44100
    samples = []
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
        "surprise": 10.56,
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
