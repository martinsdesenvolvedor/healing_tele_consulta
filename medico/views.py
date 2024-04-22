from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from . models import Especialidades, DadosMedico, is_medico, DatasAbertas
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta # timedelta para especificar dia, mes ou ano em uma conta com dadtas
from paciente.models import Consulta, Documento

# Create your views here.
@login_required
def cadastro_medico(request):
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já está cadastrado como médico.')
        return redirect('/medicos/abrir_horario')
    
    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades, 'is_medico': is_medico(request.user)})
    
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        #TODO: Validar todos os campos

        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            user=request.user,
            descricao=descricao,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta
        )
        dados_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso.')

        return redirect('/medicos/abrir_horario')
    
    
@login_required
def abrir_horario(request):
    # se o usuário não for médico, ele não poderá abrir novos horários na agenda
    if not is_medico(request.user): 
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horários!')
        return redirect('/usuarios/sair')
    
    if request.method == 'GET':
        dados_medico = DadosMedico.objects.get(user=request.user) # busca um elemento, tem so um argumento 
        datas_abertas = DatasAbertas.objects.filter(user=request.user) # filtra as datas abertas do usuario logado
        return render(request, 'abrir_horario.html', {'dados_medico': dados_medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    
    elif request.method == 'POST':
        data_atual = datetime.now()
        data = request.POST.get('data')

        if not data:
            messages.add_message(request, constants.WARNING, 'O campo Data não pode ficar vazio!')
            return redirect('/medicos/abrir_horario')

        data = datetime.strptime(data, '%Y-%m-%dT%H:%M' )

        if data <= data_atual:
            messages.add_message(request, constants.WARNING, 'Escolha uma data válida!')
            return redirect('/medicos/abrir_horario')
        
        if DatasAbertas.objects.filter(data=data).exists():
            messages.add_message(request, constants.WARNING, 'Já existe um horário com esta data!')
            return redirect('/medicos/abrir_horario')

        
        horario_abrir = DatasAbertas(
            data=data,
            user=request.user

        )
        
        horario_abrir.save()

        messages.add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso!')
        return redirect('/medicos/abrir_horario')


@login_required
def consultas_medico(request):
    # se o usuário não for médico, ele não poderá acessar sua agenda de consultas
    if not is_medico(request.user): 
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar a agenda de consultas!')
        return redirect('/usuarios/sair')
    # traz a data de hoje sem levar em consideração o horário
    hoje = datetime.now().date()
    # busca as consultas que estao em data_aberta (da agenda do medico) do usuario medico logado. Busca a data_aberta que esta em data (consulta). Busca data_aberta que esta em data (consulta) que seja maior ou igual o hoje. Busca a data_aberta que esta em data (consulta) que seja menor ou igual a amanha, que é hoje + 1
    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lte=hoje+timedelta(days=1))
    # busca as consultas restantes, excluindo as consultas que o valor do id esteja na lista das consultas de hoje
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
    
  
    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})


@login_required
def consulta_area_medico(request, id_consulta):
    # se o usuário não for médico, ele não poderá acessar uma consulta de um paciente para inicia-la
    if not is_medico(request.user): 
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar a agenda de consultas!')
        return redirect(request, 'consultas_medico.html')
    
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'documentos': documentos})
    
    elif request.method == "POST":
        # Inicializa a consulta + link da chamada
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')

        # se o usuario logado não for o medico que está na consulta, ele não consegue inicializar a consulta
        if request.user != consulta.data_aberta.user:
            messages.add_message(request, constants.ERROR, 'Somente médicos podem acessar a agenda de consultas!')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        elif consulta.status == "F":
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        # update do link e do estatus da consulta
        consulta.link = link
        consulta.status = 'I'
        consulta.save()

        messages.add_message(request, constants.SUCCESS, 'Consulta inicializada com sucesso.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    

@login_required
def finalizar_consulta(request, id_consulta):
    # se o usuário não for médico, ele não poderá finalizar uma consulta
    if not is_medico(request.user): 
        messages.add_message(request, constants.WARNING, 'Somente médicos podem finalizar consultas!')
        return redirect(request, 'consultas_medico.html')
   
    consulta = Consulta.objects.get(id=id_consulta)
    # se o usuario logado não for o medico que está na consulta, ele não consegue finalizar a consulta
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Esta consulta não é sua!')
        return redirect('/medicos/consultas_medico/')

    consulta.status = 'F'
    consulta.save()


    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
   
    
def add_documento(request, id_consulta):
    # se o usuário não for médico, ele não poderá adicionar documentos na consulta
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    # se o usuario logado não for o medico que está na consulta, ele não consegue adicionar documento na consulta
    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    if not documento:
        messages.add_message(request, constants.WARNING, 'Adicione o documento.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento

    )

    documento.save()

    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')