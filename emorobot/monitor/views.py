from django.apps import apps
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView

from .data_saver import DataType
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

def get_current_data_from_emotions(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_name = "Speech-Emotion-Analyzer"
    video_name = "video"
    audio_recognizer = receiver.emotion_data[audio_name]
    video_recognizer = receiver.emotion_data[video_name]
    audio_timestamp = receiver.timestamp_emo[audio_name]
    video_timestamp = receiver.timestamp_emo[audio_name]
    video_emotions = get_emotions_without_timestamp(video_recognizer)
    audio_emotions = get_emotions_without_timestamp(audio_recognizer)
    audio_predictions = audio_emotions.values()
    audio_labels = audio_emotions.keys()
    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": audio_timestamp,
                         "video_timestamp": video_timestamp,
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_emotions.keys()),
                         "video_recognizer_data": list(video_emotions.values()),
                         })  # http response


def get_grouped_current_data_from_emotions(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_name = "Speech-Emotion-Analyzer"
    video_name = "video"
    audio_emotions = get_emotions_without_timestamp(receiver.emotion_data[audio_name])
    audio_timestamp = receiver.timestamp_emo[audio_name]
    video_timestamp = receiver.timestamp_emo[video_name]
    audio_predictor = apps.get_app_config('monitor').audio_predictor
    video_predictor = apps.get_app_config('monitor').video_predictor
    audio_predictions, audio_labels = audio_predictor.group(audio_emotions.values(), audio_emotions.keys())
    video_emotions = get_emotions_without_timestamp(receiver.emotion_data[video_name])
    video_predictions, video_labels = video_predictor.group(video_emotions.values(), video_emotions.keys())
    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": audio_timestamp,
                         "video_timestamp": video_timestamp,
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_labels),
                         "video_recognizer_data": list(video_predictions),
                         })  # http response


def get_current_data_from_raw_data(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_name = "Speech-Emotion-Analyzer"
    video_name = "video"
    audio_predictor = apps.get_app_config('monitor').audio_predictor
    video_predictor = apps.get_app_config('monitor').video_predictor
    audio_timestamp = receiver.timestamp_raw[audio_name]
    video_timestamp = receiver.timestamp_raw[video_name]
    audio_raw_data = receiver.raw_data[audio_name]
    audio_predictions, audio_labels = audio_predictor.predict(audio_raw_data)
    video_raw_data = receiver.raw_data[video_name]
    video_predictions, video_labels = video_predictor.predict(video_raw_data)
    audio_labels, audio_predictions, video_labels, video_predictions = get_final_predictions(
        audio_labels, audio_predictions, video_labels, video_predictions)
    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": audio_timestamp,
                         "video_timestamp": video_timestamp,
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_labels),
                         "video_recognizer_data": list(video_predictions),
                         })  # http response


def get_final_predictions(audio_labels, audio_predictions, video_labels, video_predictions):
    audio_predictions = audio_predictions if audio_predictions is not None else [1.0]
    audio_labels = audio_labels if audio_labels is not None else ["no raw data"]
    video_predictions = [str(p) for p in video_predictions] if video_predictions is not None else [1.0]
    video_labels = video_labels if video_labels is not None else ["no raw data"]
    return audio_labels, audio_predictions, video_labels, video_predictions


def get_grouped_current_data_from_raw_data(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_name = "Speech-Emotion-Analyzer"
    video_name = "video"
    audio_predictor = apps.get_app_config('monitor').audio_predictor
    video_predictor = apps.get_app_config('monitor').video_predictor
    audio_timestamp = receiver.timestamp_raw[audio_name]
    video_timestamp = receiver.timestamp_raw[video_name]
    audio_raw_data = receiver.raw_data[audio_name]
    audio_predictions, audio_labels = audio_predictor.grouped_predict(audio_raw_data)
    video_raw_data = receiver.raw_data[video_name]
    video_predictions, video_labels = video_predictor.grouped_predict(video_raw_data)
    audio_labels, audio_predictions, video_labels, video_predictions = get_final_predictions(
        audio_labels, audio_predictions, video_labels, video_predictions)
    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": audio_timestamp,
                         "video_timestamp": video_timestamp,
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_labels),
                         "video_recognizer_data": list(video_predictions),
                         })  # http response


def get_emotions_without_timestamp(emotion_dict):
    dict_without_timestamp = {}
    for k, v in emotion_dict.items():
        if k != "timestamp":
            dict_without_timestamp[k] = v
    return dict_without_timestamp


def get_preview_stats_from_emotions(request, *args, **kwargs):
    return json_for_preview_stats(DataType.EMOTIONS)


def preview_stats_from_raw_data(request, *args, **kwargs):
    data_saver = apps.get_app_config('monitor').data_saver
    try:
        data_saver.get_video_data(DataType.EMOTIONS_FROM_RAW_DATA),
    except Exception as e:
        print(e)
    return json_for_preview_stats(DataType.EMOTIONS_FROM_RAW_DATA)


def json_for_preview_stats(data_type, ):
    data_saver = apps.get_app_config('monitor').data_saver
    return JsonResponse({
        "audio_recognizer_labels": data_saver.get_video_labels(data_type),
        "video_recognizer_labels": data_saver.get_audio_labels(data_type),
        "video_data": data_saver.get_video_data(data_type),
        "audio_data": data_saver.get_audio_data(data_type)
    })  # http response
