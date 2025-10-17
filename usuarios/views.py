from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    Usuario, Cidade, TipoRelacionamento, EstadoCivil, Etnia, TipoCorpo, 
    NivelAbertura, Signo, CorOlhos, CorCabelos, PerfilDetalhado, 
    PerfilInteresses, PerfilSobre
)
from .forms import (
    UsuarioRegistrationForm, UsuarioUpdateForm, PerfilUpdateForm,
    PerfilGeralForm, PerfilInformacoesForm, PerfilInteressesForm, PerfilBioForm
)


class UsuarioLoginView(LoginView):
    """View para login de usuários"""
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('feed:home')
    
    def form_valid(self, form):
        messages.success(self.request, f'Bem-vindo de volta, {form.get_user().username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Usuário ou senha inválidos.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Garantir que o formulário tenha as classes CSS corretas
        if 'form' in context:
            form = context['form']
            form.fields['username'].widget.attrs.update({'class': 'form-control'})
            form.fields['password'].widget.attrs.update({'class': 'form-control'})
        return context


def landing(request):
    """Página de boas-vindas para usuários não autenticados"""
    if request.user.is_authenticated:
        return redirect('feed:home')
    return render(request, 'usuarios/landing.html')




def logout_view(request):
    """View simples para logout de usuários"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'Você foi desconectado com sucesso.')
    return redirect('usuarios:landing')


class UsuarioRegistrationView(CreateView):
    """View para cadastro de novos usuários"""
    model = Usuario
    form_class = UsuarioRegistrationForm
    template_name = 'usuarios/cadastro.html'
    success_url = reverse_lazy('usuarios:login')
    
    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            messages.success(
                self.request, 
                'Conta criada com sucesso! Faça login para continuar.'
            )
            return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros abaixo.')
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class PerfilDetailView(DetailView):
    """View para visualizar perfil do usuário"""
    model = Usuario
    template_name = 'usuarios/perfil_proprietario.html'
    context_object_name = 'perfil'
    
    def get_object(self):
        return self.request.user


@login_required
def editar_perfil(request):
    """View para editar perfil do usuário com abas"""
    usuario = request.user
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Salvar dados básicos do usuário
                if 'username' in request.POST:
                    usuario.username = request.POST.get('username', usuario.username)
                if 'tipo_perfil' in request.POST:
                    usuario.tipo_perfil = request.POST.get('tipo_perfil', usuario.tipo_perfil)
                if 'cidade_ref' in request.POST and request.POST.get('cidade_ref'):
                    usuario.cidade_ref_id = request.POST.get('cidade_ref')
                if 'tipo_relacionamento' in request.POST and request.POST.get('tipo_relacionamento'):
                    usuario.tipo_relacionamento_id = request.POST.get('tipo_relacionamento')
                if 'tempo_juntos' in request.POST:
                    usuario.tempo_juntos = request.POST.get('tempo_juntos', '')
                usuario.save()
                
                # Salvar dados detalhados (Ele/Ela para casais)
                if usuario.tipo_perfil and usuario.tipo_perfil.startswith('casal_'):
                    # Dados do "Ele"
                    perfil_ele, created = PerfilDetalhado.objects.get_or_create(
                        usuario=usuario, pessoa='ele'
                    )
                    _salvar_dados_pessoa(request, perfil_ele, 'ele')
                    
                    # Dados da "Ela"
                    perfil_ela, created = PerfilDetalhado.objects.get_or_create(
                        usuario=usuario, pessoa='ela'
                    )
                    _salvar_dados_pessoa(request, perfil_ela, 'ela')
                else:
                    # Dados da pessoa principal (individual)
                    perfil_principal, created = PerfilDetalhado.objects.get_or_create(
                        usuario=usuario, pessoa='principal'
                    )
                    _salvar_dados_pessoa(request, perfil_principal, 'principal')
                
                # Salvar interesses
                perfil_interesses, created = PerfilInteresses.objects.get_or_create(
                    usuario=usuario
                )
                _salvar_interesses(request, perfil_interesses)
                
                # Salvar informações sobre
                perfil_sobre, created = PerfilSobre.objects.get_or_create(
                    usuario=usuario
                )
                _salvar_sobre(request, perfil_sobre, usuario.tipo_perfil)
                
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('usuarios:editar_perfil')
                
        except Exception as e:
            messages.error(request, f'Erro ao salvar perfil: {str(e)}')
    
    # Buscar dados necessários
    tipos_relacionamento = TipoRelacionamento.objects.filter(ativo=True).order_by('ordem', 'nome')
    cidades = Cidade.objects.all().order_by('nome')[:100]
    estados_civis = EstadoCivil.objects.filter(ativo=True).order_by('ordem', 'nome')
    etnias = Etnia.objects.filter(ativo=True).order_by('ordem', 'nome')
    tipos_corpo = TipoCorpo.objects.filter(ativo=True).order_by('ordem', 'nome')
    niveis_abertura = NivelAbertura.objects.filter(ativo=True).order_by('ordem', 'nome')
    signos = Signo.objects.filter(ativo=True).order_by('ordem')
    cores_olhos = CorOlhos.objects.filter(ativo=True).order_by('ordem', 'nome')
    cores_cabelos = CorCabelos.objects.filter(ativo=True).order_by('ordem', 'nome')
    
    context = {
        'tipos_relacionamento': tipos_relacionamento,
        'cidades': cidades,
        'estados_civis': estados_civis,
        'etnias': etnias,
        'tipos_corpo': tipos_corpo,
        'niveis_abertura': niveis_abertura,
        'signos': signos,
        'cores_olhos': cores_olhos,
        'cores_cabelos': cores_cabelos,
        'object': usuario,
        'user': usuario,
    }
    
    return render(request, 'usuarios/editar_perfil_limpo.html', context)

def _salvar_dados_pessoa(request, perfil, prefixo):
    """Salva dados de uma pessoa específica (ele/ela/principal)"""
    perfil.nome_apelido = request.POST.get(f'nome_{prefixo}', '')
    if request.POST.get(f'data_nascimento_{prefixo}'):
        perfil.data_nascimento = request.POST.get(f'data_nascimento_{prefixo}')
    perfil.profissao = request.POST.get(f'profissao_{prefixo}', '')
    
    if request.POST.get(f'altura_{prefixo}'):
        perfil.altura = int(request.POST.get(f'altura_{prefixo}'))
    if request.POST.get(f'peso_{prefixo}'):
        perfil.peso = int(request.POST.get(f'peso_{prefixo}'))
    
    if request.POST.get(f'signo_{prefixo}'):
        perfil.signo_id = request.POST.get(f'signo_{prefixo}')
    if request.POST.get(f'estado_civil_{prefixo}'):
        perfil.estado_civil_id = request.POST.get(f'estado_civil_{prefixo}')
    if request.POST.get(f'etnia_{prefixo}'):
        perfil.etnia_id = request.POST.get(f'etnia_{prefixo}')
    if request.POST.get(f'tipo_corpo_{prefixo}'):
        perfil.tipo_corpo_id = request.POST.get(f'tipo_corpo_{prefixo}')
    if request.POST.get(f'olhos_{prefixo}'):
        perfil.cor_olhos_id = request.POST.get(f'olhos_{prefixo}')
    if request.POST.get(f'cabelos_{prefixo}'):
        perfil.cor_cabelos_id = request.POST.get(f'cabelos_{prefixo}')
    
    perfil.orientacao_sexual = request.POST.get(f'orientacao_{prefixo}', '')
    perfil.fumante = request.POST.get(f'fumante_{prefixo}', 'nao')
    perfil.bebe = request.POST.get(f'bebe_{prefixo}', 'nao')
    perfil.descricao_pessoal = request.POST.get(f'descricao_{prefixo}', '')
    
    perfil.save()

def _salvar_interesses(request, perfil_interesses):
    """Salva interesses e preferências"""
    if request.POST.get('nivel_abertura'):
        perfil_interesses.nivel_abertura_id = request.POST.get('nivel_abertura')
    
    # Campos booleanos
    campos_booleanos = [
        'procurando_casais', 'procurando_mulheres', 'procurando_homens',
        'procurando_grupos', 'procurando_amizades', 'procurando_experiencias',
        'objetivo_amizades', 'objetivo_relacionamento', 'objetivo_troca',
        'objetivo_aventura', 'objetivo_relacao_aberta', 'objetivo_curiosidade',
        'preferencia_romantico', 'preferencia_aventureiro', 'preferencia_intimista',
        'preferencia_social', 'preferencia_privacidade', 'preferencia_publico',
        'maior_18'
    ]
    
    for campo in campos_booleanos:
        setattr(perfil_interesses, campo, campo in request.POST)
    
    perfil_interesses.save()

def _salvar_sobre(request, perfil_sobre, tipo_perfil):
    """Salva informações sobre o perfil"""
    perfil_sobre.quem_somos = request.POST.get('quem_somos', '')
    perfil_sobre.inspiracao = request.POST.get('inspiracao', '')
    perfil_sobre.frase_destaque = request.POST.get('frase_destaque', '')
    perfil_sobre.instagram = request.POST.get('instagram', '')
    perfil_sobre.outro_link = request.POST.get('outro_link', '')
    
    if tipo_perfil and tipo_perfil.startswith('casal_'):
        perfil_sobre.bio_ele = request.POST.get('bio_ele', '')
        perfil_sobre.bio_ela = request.POST.get('bio_ela', '')
    else:
        perfil_sobre.bio_individual = request.POST.get('bio_individual', '')
    
    perfil_sobre.save()


@login_required
def configuracoes(request):
    """View para configurações do usuário"""
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações atualizadas com sucesso!')
            return redirect('usuarios:configuracoes')
    else:
        form = UsuarioUpdateForm(instance=request.user)
    
    return render(request, 'usuarios/configuracoes.html', {'form': form})


@login_required
def upload_foto_perfil(request):
    """View para upload de foto de perfil via AJAX"""
    if request.method == 'POST' and request.FILES.get('foto_perfil'):
        try:
            user = request.user
            user.foto_perfil = request.FILES['foto_perfil']
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Foto de perfil atualizada com sucesso!',
                'foto_url': user.foto_perfil.url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Erro ao atualizar foto: ' + str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Nenhuma foto enviada'
    })


@login_required
def buscar_usuarios(request):
    """View para buscar usuários (para matches)"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        cidade = request.GET.get('cidade', '')
        idade_min = request.GET.get('idade_min', 18)
        idade_max = request.GET.get('idade_max', 100)
        
        usuarios = Usuario.objects.filter(is_active=True).exclude(id=request.user.id)
        
        if query:
            usuarios = usuarios.filter(
                username__icontains=query
            ) | usuarios.filter(
                first_name__icontains=query
            ) | usuarios.filter(
                last_name__icontains=query
            )
        
        if cidade:
            usuarios = usuarios.filter(cidade__icontains=cidade)
        
        # Filtro por idade
        from datetime import date, timedelta
        hoje = date.today()
        data_max = hoje - timedelta(days=int(idade_min) * 365)
        data_min = hoje - timedelta(days=int(idade_max) * 365)
        
        usuarios = usuarios.filter(
            data_nascimento__gte=data_min,
            data_nascimento__lte=data_max
        )
        
        # Aplicar filtros de preferência do usuário
        if request.user.genero_interesse:
            if request.user.genero_interesse != 'A':
                usuarios = usuarios.filter(genero=request.user.genero_interesse)
        
        usuarios = usuarios[:20]  # Limitar resultados
        
        return render(request, 'usuarios/buscar.html', {
            'usuarios': usuarios,
            'query': query,
            'cidade': cidade,
            'idade_min': idade_min,
            'idade_max': idade_max
        })
    
    return render(request, 'usuarios/buscar.html')


@login_required
def ver_perfil_usuario(request, user_id):
    """View para ver perfil de outro usuário"""
    usuario = get_object_or_404(Usuario, id=user_id, is_active=True)
    
    # Verificar se o usuário pode ver o perfil (não bloqueado, etc.)
    return render(request, 'usuarios/ver_perfil.html', {
        'perfil': usuario
    })


# ==============================================
# FLUXO DE CADASTRO GUIADO
# ==============================================

def cadastro_genero(request):
    """Etapa 1: Seleção de perfil (individual ou casal)"""
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    if request.method == 'POST':
        perfil = request.POST.get('perfil')
        
        if perfil and perfil != '':  # Ignorar separadores vazios
            # Extrair gênero do tipo de perfil para individual
            genero = None
            if perfil.startswith('individual_'):
                genero = perfil.replace('individual_', '')
                # Mapear para códigos de gênero
                genero_map = {
                    'homem': 'H',
                    'mulher': 'M', 
                    'transexual': 'T',
                    'crossdresser': 'CD',
                    'travesti': 'TV',
                    'gp_feminina': 'GP_F',
                    'gp_masculina': 'GP_M',
                }
                genero = genero_map.get(genero, 'H')
            
            # Salvar na sessão para usar nas próximas etapas
            request.session['cadastro_tipo_perfil'] = perfil
            request.session['cadastro_genero'] = genero
            return redirect('usuarios:cadastro_interesses')
        else:
            messages.error(request, 'Por favor, selecione uma opção de perfil.')
    
    return render(request, 'usuarios/cadastro_genero.html', {
        'perfil_choices': Usuario.PERFIL_CHOICES
    })


def cadastro_interesses(request):
    """Etapa 2: Seleção de interesses"""
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    tipo_perfil = request.session.get('cadastro_tipo_perfil')
    genero = request.session.get('cadastro_genero')
    
    # Verificar se tipo_perfil existe (obrigatório para todos)
    if not tipo_perfil:
        return redirect('usuarios:cadastro_genero')
    
    # Para perfis individuais, gênero é obrigatório
    if tipo_perfil.startswith('individual_') and not genero:
        return redirect('usuarios:cadastro_genero')
    
    if request.method == 'POST':
        interesses = request.POST.getlist('interesses')
        if interesses:
            request.session['cadastro_interesses'] = interesses
            return redirect('usuarios:cadastro_username')
        else:
            messages.error(request, 'Por favor, selecione pelo menos um interesse.')
    
    return render(request, 'usuarios/cadastro_interesses.html', {
        'interesse_choices': Usuario.GENERO_INTERESSE_CHOICES,
        'genero_atual': genero
    })


def cadastro_username(request):
    """Etapa 3: Nome de usuário com validação em tempo real"""
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    tipo_perfil = request.session.get('cadastro_tipo_perfil')
    genero = request.session.get('cadastro_genero')
    
    if not tipo_perfil or not request.session.get('cadastro_interesses'):
        return redirect('usuarios:cadastro_genero')
    
    # Para perfis individuais, gênero é obrigatório
    if tipo_perfil.startswith('individual_') and not genero:
        return redirect('usuarios:cadastro_genero')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            # Verificar se username já existe
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'Este nome de usuário já está em uso.')
            else:
                request.session['cadastro_username'] = username
                return redirect('usuarios:cadastro_localizacao')
        else:
            messages.error(request, 'Por favor, digite um nome de usuário.')
    
    return render(request, 'usuarios/cadastro_username.html')


@csrf_exempt
def validar_username(request):
    """AJAX: Validar disponibilidade do username em tempo real"""
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', '')
        
        if username:
            if Usuario.objects.filter(username=username).exists():
                return JsonResponse({'disponivel': False, 'message': 'Nome de usuário já em uso'})
            else:
                return JsonResponse({'disponivel': True, 'message': 'Nome de usuário disponível'})
    
    return JsonResponse({'disponivel': False, 'message': 'Nome de usuário inválido'})


def cadastro_localizacao(request):
    """Etapa 4: Localização com autocomplete e geolocalização"""
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    tipo_perfil = request.session.get('cadastro_tipo_perfil')
    genero = request.session.get('cadastro_genero')
    
    if not all([tipo_perfil, 
                request.session.get('cadastro_interesses'),
                request.session.get('cadastro_username')]):
        return redirect('usuarios:cadastro_genero')
    
    # Para perfis individuais, gênero é obrigatório
    if tipo_perfil.startswith('individual_') and not genero:
        return redirect('usuarios:cadastro_genero')
    
    if request.method == 'POST':
        cidade_nome = request.POST.get('cidade_nome', '').strip()
        estado = request.POST.get('estado', '').strip()
        latitude = request.POST.get('latitude', '0')
        longitude = request.POST.get('longitude', '0')
        cidade_completa = request.POST.get('cidade', '').strip()
        
        print(f"DEBUG - Cidade Nome: {cidade_nome}, Estado: {estado}, Cidade Completa: {cidade_completa}")
        
        if cidade_nome and estado:
            request.session['cadastro_cidade'] = cidade_nome
            request.session['cadastro_estado'] = estado
            request.session['cadastro_latitude'] = latitude
            request.session['cadastro_longitude'] = longitude
            print("DEBUG - Redirecionando para cadastro_login")
            return redirect('usuarios:cadastro_login')
        else:
            messages.error(request, 'Por favor, selecione uma cidade da lista.')
            print("DEBUG - Erro: campos vazios")
    
    return render(request, 'usuarios/cadastro_localizacao.html')


def cadastro_login(request):
    """Etapa 5: Login social (Google) ou criação de conta"""
    print(f"DEBUG - cadastro_login chamada - Method: {request.method}")
    
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    tipo_perfil = request.session.get('cadastro_tipo_perfil')
    genero = request.session.get('cadastro_genero')
    
    if not all([tipo_perfil,
                request.session.get('cadastro_interesses'),
                request.session.get('cadastro_username'),
                request.session.get('cadastro_cidade')]):
        print("DEBUG - Dados da sessão incompletos, redirecionando para cadastro_genero")
        print(f"DEBUG - tipo_perfil: {tipo_perfil}")
        print(f"DEBUG - cadastro_interesses: {request.session.get('cadastro_interesses')}")
        print(f"DEBUG - cadastro_username: {request.session.get('cadastro_username')}")
        print(f"DEBUG - cadastro_cidade: {request.session.get('cadastro_cidade')}")
        return redirect('usuarios:cadastro_genero')
    
    # Para perfis individuais, gênero é obrigatório
    if tipo_perfil.startswith('individual_') and not genero:
        return redirect('usuarios:cadastro_genero')
    
    if request.method == 'POST':
        # Processar login social ou criação de conta
        tipo_login = request.POST.get('tipo_login')
        
        if tipo_login == 'google':
            # Aqui seria integração com Google OAuth
            messages.info(request, 'Integração com Google será implementada em breve.')
            return redirect('usuarios:cadastro_foto')
        elif tipo_login == 'email':
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            
            print(f"DEBUG - Email: {email}")
            print(f"DEBUG - Password: {password}")
            print(f"DEBUG - Password2: {password2}")
            print(f"DEBUG - Passwords match: {password == password2}")
            print(f"DEBUG - Session data: {dict(request.session)}")
            
            if password == password2:
                print("DEBUG - Senhas coincidem, tentando criar usuário...")
                # Criar usuário com os dados da sessão
                try:
                    with transaction.atomic():
                        print("DEBUG - Verificando dados da sessão...")
                        print(f"DEBUG - cadastro_username: {request.session.get('cadastro_username')}")
                        print(f"DEBUG - cadastro_interesses: {request.session.get('cadastro_interesses')}")
                        print(f"DEBUG - cadastro_cidade: {request.session.get('cadastro_cidade')}")
                        print(f"DEBUG - cadastro_estado: {request.session.get('cadastro_estado')}")
                        
                        # Verificar se cadastro_interesses existe e não está vazio
                        interesses = request.session.get('cadastro_interesses', [])
                        if interesses:
                            genero_interesse = interesses[0]
                        else:
                            genero_interesse = 'H'  # Default
                        print(f"DEBUG - genero_interesse final: {genero_interesse}")
                        
                        # Determinar gênero baseado no tipo_perfil se não estiver definido
                        tipo_perfil = request.session.get('cadastro_tipo_perfil', 'individual_homem')
                        genero = request.session.get('cadastro_genero', 'H')
                        
                        print(f"DEBUG - tipo_perfil: {tipo_perfil}")
                        print(f"DEBUG - genero da sessão: {genero}")
                        
                        # Se gênero não estiver definido ou estiver vazio, extrair do tipo_perfil
                        if not genero or genero == '' or genero is None:
                            genero_map = {
                                'individual_homem': 'H',
                                'individual_mulher': 'M',
                                'individual_transexual': 'T',
                                'individual_crossdresser': 'CD',
                                'individual_travesti': 'TV',
                                'individual_gp_feminina': 'GP_F',
                                'individual_gp_masculina': 'GP_M',
                            }
                            genero = genero_map.get(tipo_perfil, 'H')
                        
                        print(f"DEBUG - genero final: {genero}")
                        
                        user = Usuario.objects.create_user(
                            username=request.session.get('cadastro_username', 'usuario_teste'),
                            email=email,
                            password=password,
                            tipo_perfil=tipo_perfil,
                            genero=genero,
                            genero_interesse=genero_interesse,
                            cidade=request.session.get('cadastro_cidade', 'São Paulo'),
                            estado=request.session.get('cadastro_estado', 'SP'),
                            latitude=float(request.session.get('cadastro_latitude', 0)) if request.session.get('cadastro_latitude') else None,
                            longitude=float(request.session.get('cadastro_longitude', 0)) if request.session.get('cadastro_longitude') else None,
                        )
                        
                        print(f"DEBUG - Usuário criado com sucesso: {user.username}")
                        
                        # Limpar sessão
                        for key in ['cadastro_tipo_perfil', 'cadastro_genero', 'cadastro_interesses', 'cadastro_username', 
                                  'cadastro_cidade', 'cadastro_estado', 'cadastro_latitude', 'cadastro_longitude']:
                            if key in request.session:
                                del request.session[key]
                        
                        # Fazer login automático
                        login(request, user)
                        messages.success(request, 'Conta criada com sucesso!')
                        print(f"DEBUG - Login realizado, redirecionando para cadastro_foto")
                        return redirect('usuarios:cadastro_foto')
                except Exception as e:
                    print(f"DEBUG - ERRO ao criar usuário: {str(e)}")
                    print(f"DEBUG - Tipo do erro: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()
                    messages.error(request, f'Erro ao criar conta: {str(e)}')
            else:
                print("DEBUG - Senhas não coincidem!")
                messages.error(request, 'As senhas não coincidem.')
    
    return render(request, 'usuarios/cadastro_login.html')


@login_required
def cadastro_foto(request):
    """Etapa 6: Upload de foto de perfil"""
    if request.method == 'POST':
        if 'foto_perfil' in request.FILES:
            try:
                # Validar tamanho do arquivo (5MB máximo)
                file = request.FILES['foto_perfil']
                if file.size > 5 * 1024 * 1024:  # 5MB
                    messages.error(request, 'Arquivo muito grande! Use uma imagem menor que 5MB.')
                    return render(request, 'usuarios/cadastro_foto.html')
                
                # Validar tipo de arquivo
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
                if file.content_type not in allowed_types:
                    messages.error(request, 'Formato não suportado! Use JPG, PNG ou WebP.')
                    return render(request, 'usuarios/cadastro_foto.html')
                
                request.user.foto_perfil = file
                request.user.save()
                messages.success(request, 'Foto de perfil adicionada com sucesso! ✨')
                return redirect('feed:home')
            except Exception as e:
                messages.error(request, f'Erro ao salvar foto: {str(e)}')
        else:
            messages.info(request, 'Você pode adicionar uma foto depois no seu perfil.')
            return redirect('feed:home')
    
    return render(request, 'usuarios/cadastro_foto.html')


def perfil_visitante(request, username):
    """Visualização de perfil para visitantes"""
    try:
        usuario = Usuario.objects.get(username=username, is_active=True)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('feed:home')
    
    # Buscar postagens do usuário
    from feed.models import Postagem
    postagens = Postagem.objects.filter(autor=usuario, is_ativo=True).order_by('-data_criacao')
    
    # Separar fotos e vídeos
    fotos = postagens.filter(tipo='image')
    videos = postagens.filter(tipo='video')
    
    return render(request, 'usuarios/perfil_visitante.html', {
        'perfil': usuario,
        'fotos': fotos,
        'videos': videos,
        'total_fotos': fotos.count(),
        'total_videos': videos.count(),
    })


def api_cidades(request):
    """API para buscar cidades - retorna JSON"""
    if request.method == 'GET':
        # Buscar todas as cidades ativas
        cidades = Cidade.objects.filter(ativa=True).order_by('estado', 'nome')
        
        # Converter para formato JSON
        cidades_data = []
        for cidade in cidades:
            cidades_data.append({
                'id': cidade.id,
                'nome': cidade.nome,
                'estado': cidade.estado,
                'latitude': float(cidade.latitude),
                'longitude': float(cidade.longitude),
                'nome_completo': cidade.nome_completo
            })
        
        return JsonResponse(cidades_data, safe=False)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
