from django.urls import path

from . import views

urlpatterns = [
    path('jobs/<int:id>/', views.ChangeJobStatusView.as_view()),
    path('jobs/', views.JobsListView.as_view()),
]
