from django.apps import apps
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.apps import apps

from emorobot.monitor.current_stats import get_predictions_and_labels
from .data_saver import DataType
from .forms import RecognitionConfigForm, SavingConfigForm
from .msq_config_sender import UpdateType

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


def is_field_empty(field):
    return field is None or field == ""

class ConfigFormView(FormView):
    form_class = RecognitionConfigForm
    template_name = 'control_panel.html'
    success_url = '/'

    def post(self, request, *args, **kwargs):
        config_sender = apps.get_app_config('monitor').config_sender
        config = {}
        question_form = self.form_class(request.POST)
        if not is_field_empty(question_form.data['send_updates']):
            config['update_cycle_on'] = question_form.data['send_updates']=='on' 
        if not is_field_empty(question_form.data['mode']):
            mode = question_form.data['mode']
            config['update_type'] = UpdateType.ALL if mode == "full_mode" else (
                UpdateType.EMOTIONS_ONLY if mode=="results_mode" else UpdateType.RAW_ONLY)
        if not is_field_empty(question_form.data['frequency']):
            config['tick_length'] = int(round(float(question_form.data['frequency'])*1000))
        config_sender.send_config(**config)
        config_form = RecognitionConfigForm(self.request.GET or None)
        saving_form = SavingConfigForm(self.request.GET or None)
        context = self.get_context_data(**kwargs)
        context['config_form'] = config_form
        context['saving_form'] = saving_form
        return render(request, self.template_name, context)
        


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
    audio_name = "Speech-Emotion-Analyzer"
    video_name = "video"
    data_type = DataType.EMOTIONS
    result = get_predictions_and_labels(audio_name, video_name, data_type)
    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": result["audio_timestamp"],
                         "video_timestamp": result["video_timestamp"],
                         "audio_recognizer_labels": list(result["audio_labels"]),
                         "audio_recognizer_data": list(result["audio_predictions"]),
                         "video_recognizer_labels": list(result["video_labels"]),
                         "video_recognizer_data": list(result["video_predictions"]),
                         })  # http response


def get_grouped_current_data_from_emotions(request, *args, **kwargs):
    audio_name = "Speech-Emotion-Analyzer"
    video_name = "video"
    data_type = DataType.EMOTIONS_GROUPED
    result = get_predictions_and_labels(audio_name, video_name, data_type)
    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": result["audio_timestamp"],
                         "video_timestamp": result["video_timestamp"],
                         "audio_recognizer_labels": list(result["audio_labels"]),
                         "audio_recognizer_data": list(result["audio_predictions"]),
                         "video_recognizer_labels": list(result["video_labels"]),
                         "video_recognizer_data": list(result["video_predictions"]),
                         })  # http response


def get_current_data_from_raw_data(request, *args, **kwargs):
    audio_name = "Speech-Emotion-Analyzer"
    video_name = "video"
    data_type = DataType.EMOTIONS_FROM_RAW_DATA
    result = get_predictions_and_labels(audio_name, video_name, data_type)
    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": result["audio_timestamp"],
                         "video_timestamp": result["video_timestamp"],
                         "audio_recognizer_labels": list(result["audio_labels"]),
                         "audio_recognizer_data": list(result["audio_predictions"]),
                         "video_recognizer_labels": list(result["video_labels"]),
                         "video_recognizer_data": list(result["video_predictions"]),
                         })  # http response


def get_grouped_current_data_from_raw_data(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_name = "Speech-Emotion-Analyzer"
    video_name = "video"
    data_type = DataType.EMOTIONS_FROM_RAW_DATA_GROUPED
    result = get_predictions_and_labels(audio_name, video_name, data_type)
    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": result["audio_timestamp"],
                         "video_timestamp": result["video_timestamp"],
                         "audio_recognizer_labels": list(result["audio_labels"]),
                         "audio_recognizer_data": list(result["audio_predictions"]),
                         "video_recognizer_labels": list(result["video_labels"]),
                         "video_recognizer_data": list(result["video_predictions"]),
                         })  # http response


def get_preview_stats_from_emotions(request, *args, **kwargs):
    return json_for_preview_stats(DataType.EMOTIONS)


def get_preview_stats_from_raw_data(request, *args, **kwargs):
    return json_for_preview_stats(DataType.EMOTIONS_FROM_RAW_DATA)


def get_grouped_preview_stats_from_emotions(request, *args, **kwargs):
    return json_for_preview_stats(DataType.EMOTIONS_GROUPED)


def get_grouped_preview_stats_from_raw_data(request, *args, **kwargs):
    return json_for_preview_stats(DataType.EMOTIONS_FROM_RAW_DATA_GROUPED)


def json_for_preview_stats(data_type):
    data_saver = apps.get_app_config('monitor').data_saver
    return JsonResponse({
        "labels": get_unique_labels(data_saver.get_video_labels(data_type),
                                    data_saver.get_audio_labels(data_type)),
        "video_data": data_saver.get_video_data(data_type),
        "audio_data": data_saver.get_audio_data(data_type)
    })  # http response


def get_unique_labels(video_labels, audio_labels):
    return list(set(video_labels + audio_labels))
