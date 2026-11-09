from django.contrib import messages
from django import forms
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, MemberForm, ProjectForm, RegisterForm, TaskCommentForm, TaskForm
from .models import Project, Task, TaskComment


PROJECTS_PER_PAGE = 9


def _member_projects(user):
    return Project.objects.filter(members=user).distinct()


def _get_project_for_member(user, project_id):
    return get_object_or_404(
        _member_projects(user)
        .select_related("owner")
        .prefetch_related("members"),
        pk=project_id,
    )


def _safe_return(request, fallback):
    target = request.POST.get("next", "")
    if target and url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(target)
    return redirect(fallback)


@login_required
def dashboard(request):
    project_list = _member_projects(request.user).select_related("owner").annotate(
        tasks_total=Count("tasks", distinct=True),
        done_total=Count(
            "tasks",
            filter=Q(tasks__status=Task.Status.DONE),
            distinct=True,
        ),
    )
    projects = Paginator(project_list, PROJECTS_PER_PAGE).get_page(
        request.GET.get("page")
    )
    return render(request, "boards/dashboard.html", {"projects": projects})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.members.add(request.user)
        messages.success(request, "Your project board is ready.")
        return redirect("project_detail", project_id=project.pk)
    return render(request, "boards/project_form.html", {"form": form})


@login_required
def project_detail(request, project_id):
    project = _get_project_for_member(request.user, project_id)
    task_list = project.tasks.select_related("assignee", "creator").annotate(
        comments_total=Count("comments", distinct=True)
    )
    tasks = list(task_list)
    lanes = [
        {
            "status": Task.Status.TODO,
            "label": "To do",
            "class_name": "lane-todo",
            "tasks": [task for task in tasks if task.status == Task.Status.TODO],
        },
        {
            "status": Task.Status.IN_PROGRESS,
            "label": "In progress",
            "class_name": "lane-doing",
            "tasks": [task for task in tasks if task.status == Task.Status.IN_PROGRESS],
        },
        {
            "status": Task.Status.DONE,
            "label": "Done",
            "class_name": "lane-done",
            "tasks": [task for task in tasks if task.status == Task.Status.DONE],
        },
    ]
    members = project.members.order_by("username")
    return render(
        request,
        "boards/project_detail.html",
        {
            "project": project,
            "lanes": lanes,
            "members": members,
            "member_form": MemberForm(),
            "task_form": TaskForm(project=project),
            "is_owner": project.owner_id == request.user.pk,
            "tasks_total": len(tasks),
            "done_total": sum(task.status == Task.Status.DONE for task in tasks),
        },
    )


@login_required
@require_POST
def add_member(request, project_id):
    project = _get_project_for_member(request.user, project_id)
    fallback = reverse("project_detail", args=[project_id])
    if project.owner_id != request.user.pk:
        messages.error(request, "Only the project owner can add members.")
        return _safe_return(request, fallback)

    form = MemberForm(request.POST)
    if form.is_valid():
        member = form.member
        if project.members.filter(pk=member.pk).exists():
            messages.info(request, f"@{member.username} is already on this team.")
        else:
            project.members.add(member)
            messages.success(request, f"@{member.username} joined the project.")
    else:
        messages.error(request, "Enter the username of an existing account.")
    return _safe_return(request, fallback)


@login_required
@require_POST
def project_delete(request, project_id):
    project = _get_project_for_member(request.user, project_id)
    if project.owner_id != request.user.pk:
        messages.error(request, "Only the project owner can delete this project.")
        return redirect("project_detail", project_id=project_id)
    project.delete()
    messages.success(request, "The project and its tasks were deleted.")
    return redirect("dashboard")


@login_required
@require_POST
def task_create(request, project_id):
    project = _get_project_for_member(request.user, project_id)
    form = TaskForm(request.POST, project=project)
    if form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.creator = request.user
        task.save()
        messages.success(request, "Task added to the board.")
    else:
        messages.error(request, "Check the task details and try again.")
    return _safe_return(request, reverse("project_detail", args=[project_id]))


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(
        Task.objects.select_related("project", "assignee", "creator"),
        pk=task_id,
        project__members=request.user,
    )
    return render(
        request,
        "boards/task_detail.html",
        {
            "task": task,
            "comment_form": TaskCommentForm(),
            "comments": task.comments.select_related("author"),
            "task_form": TaskForm(project=task.project, instance=task),
            "can_delete": task.creator_id == request.user.pk
            or task.project.owner_id == request.user.pk,
        },
    )


@login_required
@require_POST
def task_update(request, task_id):
    task = get_object_or_404(
        Task.objects.select_related("project"),
        pk=task_id,
        project__members=request.user,
    )
    form = TaskForm(request.POST, instance=task, project=task.project)
    if form.is_valid():
        form.save()
        messages.success(request, "Task details updated.")
    else:
        messages.error(request, "Check the task details and try again.")
    return _safe_return(request, reverse("task_detail", args=[task_id]))


@login_required
@require_POST
def task_delete(request, task_id):
    task = get_object_or_404(
        Task.objects.select_related("project"),
        pk=task_id,
        project__members=request.user,
    )
    if task.creator_id != request.user.pk and task.project.owner_id != request.user.pk:
        messages.error(request, "Only the task creator or project owner can delete it.")
        return redirect("task_detail", task_id=task_id)
    project_id = task.project_id
    task.delete()
    messages.success(request, "Task deleted.")
    return redirect("project_detail", project_id=project_id)


@login_required
@require_POST
def comment_create(request, task_id):
    task = get_object_or_404(
        Task.objects.select_related("project"),
        pk=task_id,
        project__members=request.user,
    )
    form = TaskCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.author = request.user
        comment.save()
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Write a comment of up to 500 characters.")
    return _safe_return(request, reverse("task_detail", args=[task_id]))


@login_required
@require_POST
def comment_delete(request, comment_id):
    comment = get_object_or_404(
        TaskComment.objects.select_related("task__project"),
        pk=comment_id,
        task__project__members=request.user,
    )
    if (
        comment.author_id != request.user.pk
        and comment.task.project.owner_id != request.user.pk
    ):
        messages.error(request, "You can only delete your own comments.")
        return redirect("task_detail", task_id=comment.task_id)
    task_id = comment.task_id
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect("task_detail", task_id=task_id)


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome. Create a project to get started.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


class SiteLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm


