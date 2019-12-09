"""Forms"""

from django import forms

MODE_CHOICES = [('results_mode', 'Only recognized emotions'),
                ('raw_data_mode', 'Only raw data'),
                ('full_mode', 'Both recognized emotions and raw data')]


class RecognitionConfigForm(forms.Form):
    """ form to set recording parameters """
    send_updates = forms.ChoiceField(required=False, 
                                                                     label="Turn sending all updates on or off:", 
                                                                     choices=[('on','on'),('off','off')], 
                                                                     widget=forms.RadioSelect, 
                                                                     initial='on')
    mode = forms.ChoiceField(required=False, 
                                                      choices=MODE_CHOICES, 
                                                      initial='results_mode', 
                                                      widget=forms.RadioSelect, 
                                                      label="Choose which data will be sent in updates:")
    frequency = forms.FloatField(required=False, 
                                                           min_value=0.1, 
                                                           help_text="seconds",
                                                           label="Update frequency:")


class SavingConfigForm(forms.Form):
    """ form to set saving parameters """
    file_name = forms.CharField()
