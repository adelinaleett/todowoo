from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, \
    AuthenticationForm  # Import user creation form & user creation form
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'todo/home.html')


def register(request):
    if request.method == 'GET':
        return render(request,
                      'todo/register.html',
                      {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Create a new user
                user = User.objects.create_user(
                    request.POST['username'],  # Username
                    password=request.POST['password1'])  # Password
                user.save()  # Save into db
                login(request, user)  # Login user
                return redirect('current')  # Redirect user to current page
            except IntegrityError:
                return render(request,
                              'todo/register.html',
                              {'form': UserCreationForm(),
                               'error': 'The username you chose has already been taken. Choose a new username.'})
        else:
            # Tell user that passwords didn't match
            return render(request,
                          'todo/register.html',
                          {'form': UserCreationForm(),
                           'error': 'Passwords did not match.'})


def loginuser(request):
    if request.method == 'GET':
        return render(request,
                      'todo/loginuser.html',
                      {'form': AuthenticationForm()})
    else:
        user = authenticate(request,
                            username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            return render(request,
                          'todo/loginuser.html',
                          {'form': AuthenticationForm(),
                           'error': 'Username and password did not match.'})
        else:
            login(request, user)  # Login user
            return redirect('current')


@login_required()
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required()
def create(request):
    if request.method == 'GET':
        return render(request, 'todo/create.html',
                      {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)  # whatever sent will be passed here
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('current')
        except ValueError:
            return render(request, 'todo/create.html',
                          {'form': TodoForm(),
                           'error': 'Bad data passed. Try again.'})


@login_required()
def current(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/current.html',
                  {'todos': todos})


@login_required()
def view(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/view.html',
                      {'todo': todo,
                       'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('current')
        except ValueError:
            return render(request,
                          'todo/view.html',
                          {'todo': todo,
                           'form': form,
                           'error': 'Bad information.'})


@login_required()
def complete(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'POST':
        todo.datecompleted = timezone.now()  # gets current time
        todo.save()  # save object
        return redirect('current')


@login_required()
def delete(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'POST':
        todo.delete()  # save object
        return redirect('current')


@login_required()
def completed(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completed.html',
                  {'todos': todos})