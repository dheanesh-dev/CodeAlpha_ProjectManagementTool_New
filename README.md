# Workroom — CodeAlpha Project Management Tool

A beginner-friendly Django project for CodeAlpha internship Task 3. Workroom helps teams organize projects on a Kanban-style board, assign tasks, track progress, and discuss work on each task.

## Features

- Register, log in, and log out
- Dashboard of projects the user belongs to
- Create projects and add registered users by username
- Project boards visible only to project members
- To Do, In Progress, and Done task lanes
- Task title, description, priority, due date, and member assignment
- Task editing and task comments
- Project owners can delete projects; task creators and owners can delete tasks
- Comment authors can delete their comments
- Responsive layout, confirmation prompts, keyboard focus styles, and empty states

Real-time notifications are an optional assignment bonus and are not included in this version.

## Requirements

- Windows 10 or 11
- Python 3.11 or newer
- VS Code recommended

## Open in VS Code

Open VS Code, choose File → Open Folder, and select CodeAlpha_ProjectManagementTool_New. Or open PowerShell in this folder and run:

    code .

## Install and run (PowerShell)

From the project folder, run:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Copy-Item .env.example .env

Generate a development key and save it to .env:

    $secret = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    (Get-Content .env) -replace '^DJANGO_SECRET_KEY=.*$', "DJANGO_SECRET_KEY=$secret" | Set-Content .env

The app reads local settings from .env. Git ignores that file. Never commit it or a real database.

If PowerShell blocks activation, use this for the current terminal window, then activate the environment again:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

## Prepare and start the app

Apply database migrations:

    python manage.py migrate

Create an administrator account if you want to use Django admin:

    python manage.py createsuperuser

Start the local development server:

    python manage.py runserver

Open http://127.0.0.1:8000/ in your browser. The admin area is at http://127.0.0.1:8000/admin/.

## First use

1. Register your account.
2. Select New project and add a name and description.
3. Use Add member to add another registered account by username.
4. Use Add a task to create a card and assign it to a team member.
5. Open a card to update its details, status, priority, due date, or assignee.
6. Add comments in the task discussion.

Only project members can open a project board or its task discussions. Project owners can delete projects. Task creators and project owners can delete tasks. Comment authors can delete their comments.

## Push to GitHub

1. Create an empty repository, for example CodeAlpha_ProjectManagementTool.
2. In GitHub Desktop choose File → Add local repository… and select this project folder.
3. Review the files. Ensure .env and db.sqlite3 are not included.
4. Commit and publish the repository.

Or use Git in PowerShell from this folder:

    git init
    git add .
    git status --short
    git commit -m "Build CodeAlpha project management tool"
    git branch -M main
    git remote add origin https://github.com/YOUR-USERNAME/CodeAlpha_ProjectManagementTool.git
    git push -u origin main

Replace YOUR-USERNAME with your GitHub username. Never add .env or db.sqlite3.

## Deployment note

This project is configured for local learning and evaluation. Before deployment, set DJANGO_DEBUG=False, configure DJANGO_ALLOWED_HOSTS for the real domain, use HTTPS, and follow Django's deployment checklist. Do not use the development server in production.

## Evaluator: clone and run from GitHub

After this repository is pushed to GitHub, the evaluator can download it by cloning it. Replace YOUR-USERNAME with the account that owns the repository:

    git clone https://github.com/YOUR-USERNAME/CodeAlpha_ProjectManagementTool.git
    cd CodeAlpha_ProjectManagementTool
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    Copy-Item .env.example .env
    $secret = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    (Get-Content .env) -replace '^DJANGO_SECRET_KEY=.*$', "DJANGO_SECRET_KEY=$secret" | Set-Content .env
    python manage.py migrate
    python manage.py runserver

The evaluator then opens http://127.0.0.1:8000/ and registers an account. To try the team workflow, they can register a second account, create a project with the first account, and add the second account to that project by username. The database and accounts are created locally during setup; no database or user password needs to be included in GitHub.
