"""Forms"""

from django import forms

MODE_CHOICES = [('results_mode', 'Only results mode'),
                ('recorded_data_mode', 'Only recorded data mode'),
                ('full_mode', 'Results and data mode')]


class RecognitionConfigForm(forms.Form):
    """ form to set recording parameters """
    mode = forms.ChoiceField(choices=MODE_CHOICES, initial='results_mode', widget=forms.RadioSelect)
    frequency = forms.IntegerField(min_value=5, help_text="in seconds")


class SavingConfigForm(forms.Form):
    """ form to set saving parameters """
    file_name = forms.CharField()
