from django.apps import apps
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.apps import apps

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
        data_saver = apps.get_app_config('monitor').data_saver
        if data_saver.directory_path is not None:
            saving_form = SavingConfigForm(self.request.GET or None, initial={'file_name': data_saver.directory_path})
        else:
            saving_form = SavingConfigForm(self.request.GET or None)
        config_form = RecognitionConfigForm(self.request.GET or None)
        context = self.get_context_data(**kwargs)
        context["is_saving"] = data_saver.save_data
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
        context["is_saving"] = data_saver.save_data
        context['config_form'] = config_form
        context['saving_form'] = saving_form
        return render(request, self.template_name, context)


# Data getters #

def get_current_data_from_emotions(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_type = "audio"
    video_type = "video"
    audio_recognizer = receiver.emotion_data[audio_type]
    video_recognizer = receiver.emotion_data[video_type]
    audio_timestamp = receiver.timestamp_emo[audio_type]
    video_timestamp = receiver.timestamp_emo[audio_type]
    video_emotions = get_emotions_without_timestamp(video_recognizer)
    audio_emotions = get_emotions_without_timestamp(audio_recognizer)
    audio_predictions = audio_emotions.values()
    audio_labels = audio_emotions.keys()
    return JsonResponse({"audio_name": receiver.names[audio_type],
                         "video_name": receiver.names[video_type],
                         "audio_timestamp": audio_timestamp,
                         "video_timestamp": video_timestamp,
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_emotions.keys()),
                         "video_recognizer_data": list(video_emotions.values()),
                         })  # http response


def get_grouped_current_data_from_emotions(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_type = "audio"
    video_type = "video"
    audio_emotions = get_emotions_without_timestamp(receiver.emotion_data[audio_type])
    audio_timestamp = receiver.timestamp_emo[audio_type]
    video_timestamp = receiver.timestamp_emo[video_type]
    audio_predictor = apps.get_app_config('monitor').audio_predictor
    video_predictor = apps.get_app_config('monitor').video_predictor
    audio_predictions, audio_labels = audio_predictor.group(audio_emotions.values(), audio_emotions.keys())
    video_emotions = get_emotions_without_timestamp(receiver.emotion_data[video_type])
    video_predictions, video_labels = video_predictor.group(video_emotions.values(), video_emotions.keys())
    return JsonResponse({"audio_name": receiver.names[audio_type],
                         "video_name": receiver.names[video_type],
                         "audio_timestamp": audio_timestamp,
                         "video_timestamp": video_timestamp,
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_labels),
                         "video_recognizer_data": list(video_predictions),
                         })  # http response


def get_current_data_from_raw_data(request, *args, **kwargs):
    receiver = apps.get_app_config('monitor').receiver
    audio_type = "audio"
    video_type = "video"
    audio_predictor = apps.get_app_config('monitor').audio_predictor
    video_predictor = apps.get_app_config('monitor').video_predictor
    audio_timestamp = receiver.timestamp_raw[audio_type]
    video_timestamp = receiver.timestamp_raw[video_type]
    audio_raw_data = receiver.raw_data[audio_type]
    audio_predictions, audio_labels = audio_predictor.predict(audio_raw_data)
    video_raw_data = receiver.raw_data[video_type]
    video_predictions, video_labels = video_predictor.predict(video_raw_data)
    audio_labels, audio_predictions, video_labels, video_predictions = get_final_predictions(
        audio_labels, audio_predictions, video_labels, video_predictions)
    return JsonResponse({"audio_name": audio_predictor.get_name(),
                         "video_name": video_predictor.get_name(),
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
    audio_type = "audio"
    video_type = "video"
    audio_predictor = apps.get_app_config('monitor').audio_predictor
    video_predictor = apps.get_app_config('monitor').video_predictor
    audio_timestamp = receiver.timestamp_raw[audio_type]
    video_timestamp = receiver.timestamp_raw[video_type]
    audio_raw_data = receiver.raw_data[audio_type]
    audio_predictions, audio_labels = audio_predictor.grouped_predict(audio_raw_data)
    video_raw_data = receiver.raw_data[video_type]
    video_predictions, video_labels = video_predictor.grouped_predict(video_raw_data)
    audio_labels, audio_predictions, video_labels, video_predictions = get_final_predictions(
        audio_labels, audio_predictions, video_labels, video_predictions)
    return JsonResponse({"audio_name": audio_predictor.get_name(),
                         "video_name": video_predictor.get_name(),
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
    data_saver = apps.get_app_config('monitor').data_saver
    return json_for_preview_stats(DataType.EMOTIONS, data_saver, data_saver.audio.robot_NN_name,
                                  data_saver.video.robot_NN_name)


def get_preview_stats_from_raw_data(request, *args, **kwargs):
    data_saver = apps.get_app_config('monitor').data_saver
    return json_for_preview_stats(DataType.EMOTIONS_FROM_RAW_DATA, data_saver, data_saver.audio.robot_NN_name,
                                  data_saver.video.robot_NN_name)


def get_grouped_preview_stats_from_emotions(request, *args, **kwargs):
    data_saver = apps.get_app_config('monitor').data_saver
    return json_for_preview_stats(DataType.EMOTIONS_GROUPED, data_saver, data_saver.audio.local_NN_name,
                                  data_saver.video.local_NN_name)


def get_grouped_preview_stats_from_raw_data(request, *args, **kwargs):
    data_saver = apps.get_app_config('monitor').data_saver
    try:
        return json_for_preview_stats(DataType.EMOTIONS_FROM_RAW_DATA_GROUPED, data_saver, data_saver.audio.local_NN_name,
                                  data_saver.video.local_NN_name)
    except Exception as e:
        print(str(e))


def json_for_preview_stats(data_type, data_saver, audio_name, video_name):
    return JsonResponse({
        "audio_name": audio_name,
        "video_name": video_name,
        "labels": get_unique_labels(data_saver.get_video_labels(data_type), data_saver.get_audio_labels(data_type)),
        "video_data": data_saver.get_video_data(data_type),
        "audio_data": data_saver.get_audio_data(data_type)
    })  # http response


def get_unique_labels(video_labels, audio_labels):
    return list(set(video_labels + audio_labels))
