from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def logar(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(request, username=username, password=senha)
        
        if user:
            login(request, user)
            messages.add_message(request, constants.SUCCESS, 'Usuário logado com sucesso!')
            return redirect('/pacientes/home')
        
        
        messages.add_message(request, constants.ERROR, 'Usuário ou Senha Inválido, Tente Novamente!')
        return redirect('/usuarios/login')


def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não são Iguais!')
            return redirect('/usuarios/cadastro')
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'A senha deve ter no mínimo 6 caracteres!')
            return redirect('/usuarios/cadastro')
        
        if User.objects.filter(username=username).exists():
            messages.add_message(request, constants.ERROR, 'Já existe um Usuário cadastrado com este Username!')
            return redirect('/usuarios/cadastro')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )

        messages.add_message(request, constants.SUCCESS, 'Usuário Cadastrado com Sucesso!')
        return redirect('/usuarios/login')
    


def deslogar(request):
    logout(request)
    return redirect('/usuarios/login')