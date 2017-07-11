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

		#if form.is_valid():
		street = request.GET.get('street')
		segment = request.GET.get('segment')
		date = request.GET.get('date')
		time = request.GET.get('time')

		prediction = traffic_model.get_prediction(street, segment, date, time)

		return HttpResponse(prediction)
		#else:
		#	return HttpResponse("Something happened")
	else:
		return HttpResponse("Something Happened at start")

def init(request):
	traffic_model.initialize_tree()
	return HttpResponse("Tree initialized.")
