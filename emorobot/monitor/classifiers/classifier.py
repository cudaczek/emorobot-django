from abc import ABC


class Classifier(ABC):
    def __init__(self):
        self.neural_net = None

    def predict(self, raw_data):
        raise NotImplementedError("Should be implemented in specific class")

    def grouped_predict(self, raw_data):
        if raw_data != b'':
            audio_predictions, audio_labels = self.predict(raw_data)
            return self.group(audio_predictions, audio_labels)
        else:
            return None, None

    def group(self, predictions, labels):
        groups_names = self.neural_net.grouped_emotions.keys()
        groups = self.neural_net.grouped_emotions
        grouped_emotions = dict()
        for group_name in groups_names:
            grouped_emotions.update({group_name: 0.0})
        grouped_emotions.update({"other": 0.0})
        if predictions is not None and labels is not None:
            for pred, label in zip(predictions, labels):
                added = False
                for group_name in groups_names:
                    if label in groups[group_name]:
                        grouped_emotions[group_name] += pred
                        added = True
                if not added:
                    grouped_emotions["other"] += pred
            return grouped_emotions.values(), grouped_emotions.keys()
        else:
            return [], []
