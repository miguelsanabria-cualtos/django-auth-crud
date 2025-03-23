from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Usuario ya existe'})
        return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Los passwords no coinciden'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html', {'form': AuthenticationForm(), 'error': 'Usuario y password no coinciden'})
        else:
            login(request, user)
            return redirect('tasks')


@login_required
def logoutuser(request):
    logout(request)
    return redirect('home')


@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('tasks')
    else:
        return render(request, 'create_task.html', {'form': TaskForm()})


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted=None)
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def task_detail(request, task_pk):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_pk, user=request.user)
        task_form = TaskForm(request.POST, instance=task)
        if task_form.is_valid():
            task_form.save()
            return redirect('tasks')
    else:
        task = get_object_or_404(Task, pk=task_pk, user=request.user)
        task_form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': task_form})


@login_required
def task_complete(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')
    else:
        return render(request, 'task_complete.html', {'task': task})


@login_required
def task_delete(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
    else:
        return render(request, 'task_delete.html', {'task': task})


@login_required
def task_completed(request):
    tasks = Task.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})
