from django.shortcuts import render, redirect
from tasties_app.models import Recipe, Rating
from django.db.models import Avg
from collections import OrderedDict
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
from django.contrib import messages


@login_required(login_url='login')
def index(request):
    return render(request, 'tasties_app/index.html',)


def base(request):
    return render(request, 'tasties_app/base.html',)


def recipes(request):
    recipes_list = Recipe.objects.all()
    recipes_with_ratings = {}
    for recipe in recipes_list:
        recipes_with_ratings[recipe] = Rating.objects.filter(recipe_id=recipe).aggregate(Avg('rating'))['rating__avg']
    recipes_with_ratings = OrderedDict(sorted(recipes_with_ratings.items(), key=lambda x: x[1], reverse=True))
    context = {'recipes_with_ratings': recipes_with_ratings}
    return render(request, 'tasties_app/recipes.html', context)


def login_user(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Username OR password is incorrect')
    return render(request, 'tasties_app/login.html',)


def logout_user(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')
        else:
            messages.error(request, form.error_messages)

    context = {'form': form}
    return render(request, 'tasties_app/register.html', context)
