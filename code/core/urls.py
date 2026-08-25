from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("placement/", views.placement_list, name="placement_list"),
    path("placement/companies/new/", views.company_create, name="company_create"),
    path("placement/rounds/new/", views.round_create, name="round_create"),
    path("placement/rounds/<int:pk>/", views.round_detail, name="round_detail"),
    path("placement/rounds/<int:pk>/publish/", views.round_publish, name="round_publish"),
    path("placement/rounds/<int:pk>/checklist/new/", views.checklist_create, name="checklist_create"),
    path("placement/checklist/<int:pk>/toggle/", views.checklist_toggle, name="checklist_toggle"),
    path("academics/", views.assignment_list, name="assignment_list"),
    path("academics/new/", views.assignment_create, name="assignment_create"),
    path("academics/<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("academics/<int:pk>/submit/", views.assignment_submit, name="assignment_submit"),
    path("submissions/<int:pk>/", views.submission_detail, name="submission_detail"),
    path("submissions/<int:pk>/download/", views.submission_download, name="submission_download"),
    path("submissions/<int:pk>/review/", views.submission_review, name="submission_review"),
    path("submissions/<int:pk>/grade/", views.submission_grade, name="submission_grade"),
]
