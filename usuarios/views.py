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

from .models import Usuario
from .forms import UsuarioRegistrationForm, UsuarioUpdateForm, PerfilUpdateForm


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


@method_decorator(login_required, name='dispatch')
class PerfilUpdateView(UpdateView):
    """View para editar perfil do usuário"""
    model = Usuario
    form_class = PerfilUpdateForm
    template_name = 'usuarios/editar_perfil.html'
    success_url = reverse_lazy('usuarios:perfil')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros abaixo.')
        return super().form_invalid(form)


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
    """Etapa 1: Seleção de gênero"""
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    if request.method == 'POST':
        genero = request.POST.get('genero')
        if genero:
            # Salvar na sessão para usar nas próximas etapas
            request.session['cadastro_genero'] = genero
            return redirect('usuarios:cadastro_interesses')
        else:
            messages.error(request, 'Por favor, selecione um gênero.')
    
    return render(request, 'usuarios/cadastro_genero.html', {
        'genero_choices': Usuario.GENERO_CHOICES
    })


def cadastro_interesses(request):
    """Etapa 2: Seleção de interesses"""
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    genero = request.session.get('cadastro_genero')
    if not genero:
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
    
    if not request.session.get('cadastro_genero') or not request.session.get('cadastro_interesses'):
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
    
    if not all([request.session.get('cadastro_genero'), 
                request.session.get('cadastro_interesses'),
                request.session.get('cadastro_username')]):
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
    if request.user.is_authenticated:
        return redirect('feed:home')
    
    if not all([request.session.get('cadastro_genero'),
                request.session.get('cadastro_interesses'),
                request.session.get('cadastro_username'),
                request.session.get('cadastro_cidade')]):
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
            
            if password == password2:
                # Criar usuário com os dados da sessão
                try:
                    with transaction.atomic():
                        user = Usuario.objects.create_user(
                            username=request.session['cadastro_username'],
                            email=email,
                            password=password,
                            genero=request.session['cadastro_genero'],
                            genero_interesse=request.session['cadastro_interesses'][0] if request.session['cadastro_interesses'] else '',
                            cidade=request.session['cadastro_cidade'],
                            estado=request.session['cadastro_estado'],
                            latitude=float(request.session['cadastro_latitude']) if request.session['cadastro_latitude'] else None,
                            longitude=float(request.session['cadastro_longitude']) if request.session['cadastro_longitude'] else None,
                        )
                        
                        # Limpar sessão
                        for key in ['cadastro_genero', 'cadastro_interesses', 'cadastro_username', 
                                  'cadastro_cidade', 'cadastro_estado', 'cadastro_latitude', 'cadastro_longitude']:
                            if key in request.session:
                                del request.session[key]
                        
                        # Fazer login automático
                        login(request, user)
                        messages.success(request, 'Conta criada com sucesso!')
                        return redirect('usuarios:cadastro_foto')
                except Exception as e:
                    messages.error(request, f'Erro ao criar conta: {str(e)}')
            else:
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
