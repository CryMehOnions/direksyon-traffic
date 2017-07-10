from django.shortcuts import render
from django.http import HttpResponse
from TrafficModel.forms import PredictionForm
from TrafficModel import traffic_model
# Create your views here.

def index(request):
	return HttpResponse("Hello World")

def getPrediction(request):
	if request.method == 'GET':
		form = PredictionForm(request)

		if form.is_valid():
			street = form.cleaned_data['street']
			segment = form.cleaned_data['segment']
			date = form.cleaned_data['date']
			time = form.cleaned_data['time']

			print getPrediction(street, segment, date, time)
		else:
			print "Something happened"
	else:
		print "Something Happened at start"
