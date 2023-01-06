from django.urls import path

from . import views

urlpatterns = [
    path('blacklist/company/', views.BlacklistCompanyView.as_view()),
]
