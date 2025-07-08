from django.urls import path
from . import views

urlpatterns = [
    path('', views.instrument_selector, name='instrument_selector'),
]