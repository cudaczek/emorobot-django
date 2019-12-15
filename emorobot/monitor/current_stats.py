from django.apps import apps
from django.http import JsonResponse

from .data_saver import DataType


def get_results_and_labels(audio_type, video_type, data_type):
    receiver = apps.get_app_config('monitor').receiver
    audio_recognizer = receiver.emotion_data[audio_type]
    video_recognizer = receiver.emotion_data[video_type]
    audio_predictor = apps.get_app_config('monitor').audio_classifier
    video_predictor = apps.get_app_config('monitor').video_classifier
    if data_type == DataType.EMOTIONS:
        results = (get_received_emotions_from_robot(audio_recognizer, video_recognizer), receiver.names[audio_type],
                   receiver.names[video_type])
    elif data_type == DataType.EMOTIONS_GROUPED:
        results = get_received_emotions_from_robot(audio_recognizer, video_recognizer)
        results = (group_results_and_labels(results, audio_predictor, video_predictor), receiver.names[audio_type],
                   receiver.names[video_type])
    elif data_type == DataType.EMOTIONS_FROM_RAW_DATA:
        results = get_classified_emotions(audio_type, audio_predictor, receiver, video_type, video_predictor)
        results = (get_final_classification(results), audio_predictor.get_name(), video_predictor.get_name())
    elif data_type == DataType.EMOTIONS_FROM_RAW_DATA_GROUPED:
        results = get_classified_emotions(audio_type, audio_predictor, receiver, video_type, video_predictor)
        results = group_results_and_labels(results, audio_predictor, video_predictor)
        results = get_final_classification(results), audio_predictor.get_name(), video_predictor.get_name()
    else:
        raise AttributeError
    (audio_labels, audio_results, video_labels, video_results), audio_name, video_name = results
    audio_timestamp, video_timestamp = get_timestamps(receiver, audio_type, video_type, data_type)

    return JsonResponse({"audio_name": audio_name,
                         "video_name": video_name,
                         "audio_timestamp": audio_timestamp,
                         "video_timestamp": video_timestamp,
                         "audio_recognizer_labels": list(audio_labels),
                         "audio_recognizer_data": list(audio_results),
                         "video_recognizer_labels": list(video_labels),
                         "video_recognizer_data": list(video_results),
                         })  # http response


def get_classified_emotions(audio_name, audio_predictor, receiver, video_name, video_predictor):
    audio_raw_data = receiver.raw_data[audio_name]
    video_raw_data = receiver.raw_data[video_name]
    audio_results, audio_labels = audio_predictor.classify(audio_raw_data)
    video_results, video_labels = video_predictor.classify(video_raw_data)
    return audio_labels, audio_results, video_labels, video_results


def group_results_and_labels(results, audio_predictor, video_predictor):
    audio_labels, audio_results, video_labels, video_results = results
    audio_results, audio_labels = audio_predictor.group(audio_results, audio_labels)
    video_results, video_labels = video_predictor.group(video_results, video_labels)
    return audio_labels, audio_results, video_labels, video_results


def get_received_emotions_from_robot(audio_recognizer, video_recognizer):
    audio_results, audio_labels = get_emotions_without_timestamp(audio_recognizer)
    video_results, video_labels = get_emotions_without_timestamp(video_recognizer)
    return audio_labels, audio_results, video_labels, video_results


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


def get_final_classification(results):
    audio_labels, audio_results, video_labels, video_results = results
    audio_results = audio_results if audio_results is not None else [1.0]
    audio_labels = audio_labels if audio_labels is not None else ["no raw data"]
    video_results = [str(p) for p in video_results] if video_results is not None else [1.0]
    video_labels = video_labels if video_labels is not None else ["no raw data"]
    return audio_labels, audio_results, video_labels, video_results


def get_emotions_without_timestamp(emotion_dict):
    if "timestamp" in emotion_dict:
        del emotion_dict["timestamp"]
    return emotion_dict.values(), emotion_dict.keys()
