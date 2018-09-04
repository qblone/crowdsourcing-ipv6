import re

from django import forms

from django.core import validators

from django.core.exceptions import ValidationError
from django.forms import URLField
from django.forms import GenericIPAddressField


class SubmitResults(forms.Form):
    error_messages = {
        'Invalid_URL': 'Please enter correct URL'
    }

    prefix = 'aform_pre'
    proa_value = forms.CharField(required=False, widget=forms.HiddenInput(), max_length=50)
    v4dns = forms.GenericIPAddressField(required=False, widget=forms.HiddenInput())
    v6dns = forms.GenericIPAddressField(required=False, widget=forms.HiddenInput())
    ipds = forms.GenericIPAddressField(protocol='both', required=False, widget=forms.HiddenInput())  # change this
    ipdslp = forms.GenericIPAddressField(protocol='both', required=False, widget=forms.HiddenInput())
    v4nodns = forms.GenericIPAddressField(required=False, widget=forms.HiddenInput())
    v6nodns = forms.GenericIPAddressField(protocol='IPv6', required=False, widget=forms.HiddenInput())
    v6ispdns = forms.GenericIPAddressField(protocol='both', required=False, widget=forms.HiddenInput())
    v6mtu = forms.GenericIPAddressField(protocol='both', required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(SubmitResults, self).clean()

        proa_value = self.cleaned_data.get('proa_value')
        v4dns = self.cleaned_data.get('v4dns')
        v6dns = self.cleaned_data.get('v6dns', 0)
        ipds = self.cleaned_data.get('ipds', 0)
        ipdslp = self.cleaned_data.get('ipdslp', 0)
        v4nodns = self.cleaned_data.get('v4nodns')
        v6nodns = self.cleaned_data.get('v6nodns', 0)
        v6mtu = self.cleaned_data.get('v6mtu', 0)
        v6ispdns = self.cleaned_data.get('v6ispdns', 0)
        # Remember to always return the cleaned data.
        return cleaned_data
