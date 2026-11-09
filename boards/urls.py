from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("projects/new/", views.project_create, name="project_create"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path("projects/<int:project_id>/members/add/", views.add_member, name="add_member"),
    path("projects/<int:project_id>/delete/", views.project_delete, name="project_delete"),
    path("projects/<int:project_id>/tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("tasks/<int:task_id>/update/", views.task_update, name="task_update"),
    path("tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),
    path("tasks/<int:task_id>/comments/", views.comment_create, name="comment_create"),
    path("comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
    path("register/", views.register, name="register"),
    path("login/", views.SiteLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
