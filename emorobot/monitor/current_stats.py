from django.apps import apps
from django.http import JsonResponse

from .data_saver import DataType


def get_predictions_and_labels(audio_type, video_type, data_type):
    receiver = apps.get_app_config('monitor').receiver
    audio_recognizer = receiver.emotion_data[audio_type]
    video_recognizer = receiver.emotion_data[video_type]
    audio_predictor = apps.get_app_config('monitor').audio_predictor
    video_predictor = apps.get_app_config('monitor').video_predictor
    if data_type == DataType.EMOTIONS:
        results = (get_received_emotions_from_robot(audio_recognizer, video_recognizer), receiver.names[audio_type],
                   receiver.names[video_type])
    elif data_type == DataType.EMOTIONS_GROUPED:
        results = get_received_emotions_from_robot(audio_recognizer, video_recognizer)
        results = (group_predictions_and_labels(results, audio_predictor, video_predictor), receiver.names[audio_type],
                   receiver.names[video_type])
    elif data_type == DataType.EMOTIONS_FROM_RAW_DATA:
        results = get_predicted_emotions(audio_type, audio_predictor, receiver, video_type, video_predictor)
        results = (get_final_predictions(results), audio_predictor.get_name(), video_predictor.get_name())
    elif data_type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
        results = get_predicted_emotions(audio_type, audio_predictor, receiver, video_type, video_predictor)
        results = group_predictions_and_labels(results, audio_predictor, video_predictor)
        results = get_final_predictions(results), audio_predictor.get_name(), video_predictor.get_name()
    else:
        raise AttributeError
    (audio_labels, audio_predictions, video_labels, video_predictions), audio_name, video_name = results
    audio_timestamp, video_timestamp = get_timestamps(receiver, audio_type, video_type, data_type)

    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": audio_timestamp,
                         "video_timestamp": video_timestamp,
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_predictions),
                         "video_recognizer_labels": list(video_labels),
                         "video_recognizer_data": list(video_predictions),
                         })  # http response


def get_predicted_emotions(audio_name, audio_predictor, receiver, video_name, video_predictor):
    audio_raw_data = receiver.raw_data[audio_name]
    video_raw_data = receiver.raw_data[video_name]
    audio_predictions, audio_labels = audio_predictor.predict(audio_raw_data)
    video_predictions, video_labels = video_predictor.predict(video_raw_data)
    return audio_labels, audio_predictions, video_labels, video_predictions


def group_predictions_and_labels(results, audio_predictor, video_predictor):
    audio_labels, audio_predictions, video_labels, video_predictions = results
    audio_predictions, audio_labels = audio_predictor.group(audio_predictions, audio_labels)
    video_predictions, video_labels = video_predictor.group(video_predictions, video_labels)
    return audio_labels, audio_predictions, video_labels, video_predictions


def get_received_emotions_from_robot(audio_recognizer, video_recognizer):
    audio_predictions, audio_labels = get_emotions_without_timestamp(audio_recognizer)
    video_predictions, video_labels = get_emotions_without_timestamp(video_recognizer)
    return audio_labels, audio_predictions, video_labels, video_predictions


def get_timestamps(receiver, audio_name, video_name, data_type):
    if data_type == DataType.EMOTIONS_FROM_RAW_DATA or data_type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
        audio_timestamp = receiver.timestamp_raw[audio_name]
        video_timestamp = receiver.timestamp_raw[video_name]
    elif data_type == DataType.EMOTIONS_GROUPED or data_type == DataType.EMOTIONS:
        audio_timestamp = receiver.timestamp_emo[audio_name]
        video_timestamp = receiver.timestamp_emo[video_name]
    else:
        raise AttributeError
    return audio_timestamp, video_timestamp


def get_final_predictions(results):
    audio_labels, audio_predictions, video_labels, video_predictions = results
    audio_predictions = audio_predictions if audio_predictions is not None else [1.0]
    audio_labels = audio_labels if audio_labels is not None else ["no raw data"]
    video_predictions = [str(p) for p in video_predictions] if video_predictions is not None else [1.0]
    video_labels = video_labels if video_labels is not None else ["no raw data"]
    return audio_labels, audio_predictions, video_labels, video_predictions


def get_emotions_without_timestamp(emotion_dict):
    if "timestamp" in emotion_dict:
        del emotion_dict["timestamp"]
    return emotion_dict.values(), emotion_dict.keys()
