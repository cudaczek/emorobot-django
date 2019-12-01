import datetime

from django.apps import apps
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView

from .forms import RecognitionConfigForm, SavingConfigForm

User = get_user_model()


def index(request):
    return render(request, "index.html")


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

def get_current_data_from_emotions(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_recognizer = receiver.emotion_data["Speech-Emotion-Analyzer"]
    audio_predictions = audio_recognizer.values()
    audio_labels = audio_recognizer.keys()
    video_recognizer = receiver.emotion_data["video"]
    return JsonResponse({"audio_name": "Speech-Emotion-Analyzer",
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_recognizer.keys()),
                         "video_recognizer_data": list(video_recognizer.values()),
                         })  # http response


def get_current_data_from_raw_data(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_predictor = apps.get_app_config('monitor').audio_predictor
    video_predictor = apps.get_app_config('monitor').video_predictor
    audio_raw_data = receiver.raw_data["Speech-Emotion-Analyzer"]
    audio_predictions, audio_labels = audio_predictor.predict(audio_raw_data)
    audio_predictions = audio_predictions if audio_predictions is not None else [1.0]
    audio_labels = audio_labels if audio_labels is not None else ["no raw data"]
    video_raw_data = receiver.raw_data["video"]
    video_predictions, video_labels = video_predictor.predict(video_raw_data)
    video_predictions = [str(p) for p in video_predictions] if video_predictions is not None else [1.0]
    video_labels = video_labels if video_labels is not None else ["no raw data"]
    return JsonResponse({"audio_name": "Speech-Emotion-Analyzer",
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_labels),
                         "video_recognizer_data": list(video_predictions),
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
