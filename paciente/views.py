from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from paciente.models import Consulta, Documento
from datetime import datetime
from django.contrib import messages
from django.contrib.messages import constants

# Create your views here.
@login_required
def home(request):
    if request.method == 'GET':
        # buscando os campos selecionados pelo usuário
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')

        # busca todos os médicos
        medicos = DadosMedico.objects.all()

        if medico_filtrar:
            # a letra que o usuário digitar que tiver no nome do médico vai trazer todos os médicos com estas letras, devido uso do icontains
            medicos = medicos.filter(nome__icontains=medico_filtrar)

        if especialidades_filtrar:
            # vai buscar todos os medicos que tem a(s) especialidade(s) que o usuário selecionou
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)

        especialidades = Especialidades.objects.all()

        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades, 'is_medico': is_medico(request.user)})
    
 
@login_required    
def escolher_horario(request, id_dados_medicos):
    if request.method == 'GET':
        # busca o medico no banco de dados pelo id_dados_medicos passado na url
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        # filtra pelo usuário buscado no banco de dados atraves do id_dados_medicos
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
       
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    
        
@login_required
def agendar_horario(request, id_data_aberta):
    if request.method == 'GET':
        # busca no banco de dados todas as datas abertas com id_agendar_horario passado na url
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
        # cria uma consulta com data_aberta recebido que ainda é False
        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta

        )

        # salva no banco de dados
        horario_agendado.save()
        # faz um update de data_aberta
        data_aberta.agendado = True
        # salva a alteração feita
        data_aberta.save()

        messages.add_message(request, constants.SUCCESS, 'Consulta Agendada com Sucesso!')
        return redirect('/pacientes/minhas_consultas/')
    

@login_required
def minhas_consultas(request):
    # fazer os filtros tarefa de casa

    if request.method == 'GET':
        # busca no banco de dados todas as consultas do paciente logado, somente as que a data_aberta estejam em data (data da consulta) da tabela DatasAbertas, pois data_aberta é forikey com a tabela DatasAbertas, e que são iguais ou maiores que a data do dia atual
        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})
    

def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user) # usario (medico) é igual o id consulta, que tem o data_aberta atrelada ao usuario que é o medico. Pela data_aberta eu consigo buscar o medico, pois cada data aberta pertence a um id de medico
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'documentos': documentos})
    

# criar a view de finalizar consulta. verificar se o paciente logado é o paciente da consulta