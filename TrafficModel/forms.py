from django import forms

class PredictionForm(forms.Form):
	street = forms.CharField(max_length=256)
	segment = forms.CharField(max_length=256)
	date = forms.CharField(max_length=256)
	time = forms.CharField(max_length=256)