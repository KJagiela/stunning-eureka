from django.urls import path

from . import views

urlpatterns = [
    path('job/<int:id>/', views.ChangeJobStatusView.as_view()),
    path('company/<int:id>/', views.ChangeCompanyStatusView.as_view()),
    path('jobs/', views.JobsListView.as_view()),
]
