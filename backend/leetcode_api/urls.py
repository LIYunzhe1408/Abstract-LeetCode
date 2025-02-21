from django.urls import path
from .views import  solve_question_api
from .views import download_excel

urlpatterns = [
    path("solve/", solve_question_api, name="solve_question_api"),
    path("download/", download_excel, name="download_excel"),
]
