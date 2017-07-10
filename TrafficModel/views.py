from django.shortcuts import render
from django.http import HttpResponse
from TrafficModel.forms import PredictionForm
from TrafficModel import traffic_model
# Create your views here.

def index(request):
	return HttpResponse("Hello World")

def getPrediction(request):
	if request.method == 'GET':
		#form = PredictionForm(request)

		street = request.data['street']
		segment = request.data['segment']
		date = request.data['date']
		time = request.data['time']

		prediction = getPrediction(street, segment, date, time)

		return HttpResponse(prediction)
	else:
		return HttpResponse("Something Happened at start")
