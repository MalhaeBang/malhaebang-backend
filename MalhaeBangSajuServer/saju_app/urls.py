# urls.py
from django.urls import path
from .views import index, result_view

urlpatterns = [
    path('', index, name='index'),
    path('result/', result_view, name='result'),
]

