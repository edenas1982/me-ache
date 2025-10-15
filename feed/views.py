from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Postagem, Curtida, Comentario, Relacionamento
from .forms import PostagemForm, ComentarioForm


@login_required
def home(request):
    """Página inicial do feed"""
    postagens = Postagem.objects.filter(is_ativo=True).select_related('autor').prefetch_related('curtidas', 'comentarios')
    
    # Paginação
    paginator = Paginator(postagens, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'postagens': page_obj,
        'form': PostagemForm(),
    }
    
    return render(request, 'feed/home.html', context)


@login_required
def explorar(request):
    """Página de exploração de usuários"""
    # Buscar usuários compatíveis
    usuarios = buscar_usuarios_compatíveis(request.user)
    
    context = {
        'usuarios': usuarios,
    }
    
    return render(request, 'feed/explorar.html', context)


@login_required
def criar_postagem(request):
    """Criar nova postagem"""
    if request.method == 'POST':
        form = PostagemForm(request.POST, request.FILES)
        if form.is_valid():
            postagem = form.save(commit=False)
            postagem.autor = request.user
            postagem.save()
            
            messages.success(request, 'Postagem criada com sucesso!')
            return redirect('feed:home')
    else:
        form = PostagemForm()
    
    return render(request, 'feed/criar_postagem.html', {'form': form})


@login_required
def detalhes_postagem(request, post_id):
    """Detalhes de uma postagem específica"""
    postagem = get_object_or_404(Postagem, id=post_id, is_ativo=True)
    comentarios = postagem.comentarios.filter(is_ativo=True).select_related('usuario')
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.postagem = postagem
            comentario.save()
            
            messages.success(request, 'Comentário adicionado!')
            return redirect('feed:detalhes_postagem', post_id=post_id)
    else:
        form = ComentarioForm()
    
    context = {
        'postagem': postagem,
        'comentarios': comentarios,
        'form': form,
    }
    
    return render(request, 'feed/detalhes_postagem.html', context)


@login_required
@require_http_methods(["POST"])
def curtir_postagem(request, post_id):
    """Curtir/descurtir postagem via AJAX"""
    postagem = get_object_or_404(Postagem, id=post_id)
    
    try:
        curtida, created = Curtida.objects.get_or_create(
            usuario=request.user,
            postagem=postagem
        )
        
        if not created:
            curtida.delete()
            liked = False
        else:
            liked = True
        
        total_curtidas = postagem.total_curtidas
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': total_curtidas
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def comentar_postagem(request, post_id):
    """Comentar postagem via AJAX"""
    postagem = get_object_or_404(Postagem, id=post_id)
    
    try:
        conteudo = request.POST.get('conteudo', '').strip()
        if not conteudo:
            return JsonResponse({
                'success': False,
                'error': 'Comentário não pode estar vazio'
            })
        
        comentario = Comentario.objects.create(
            usuario=request.user,
            postagem=postagem,
            conteudo=conteudo
        )
        
        return JsonResponse({
            'success': True,
            'comentario': {
                'id': comentario.id,
                'usuario': comentario.usuario.username,
                'conteudo': comentario.conteudo,
                'data_criacao': comentario.data_criacao.strftime('%d/%m/%Y %H:%M')
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def buscar_usuarios_compatíveis(usuario):
    """Buscar usuários compatíveis para matches"""
    from usuarios.models import Usuario
    
    # Filtrar usuários ativos, diferentes do usuário atual
    usuarios = Usuario.objects.filter(is_active=True).exclude(id=usuario.id)
    
    # Aplicar filtros de preferência
    if usuario.genero_interesse and usuario.genero_interesse != 'A':
        usuarios = usuarios.filter(genero=usuario.genero_interesse)
    
    # Filtro por idade
    if usuario.idade_minima and usuario.idade_maxima:
        from datetime import date, timedelta
        hoje = date.today()
        data_max = hoje - timedelta(days=usuario.idade_minima * 365)
        data_min = hoje - timedelta(days=usuario.idade_maxima * 365)
        
        usuarios = usuarios.filter(
            data_nascimento__gte=data_min,
            data_nascimento__lte=data_max
        )
    
    # Filtro por localização (se configurado)
    if usuario.cidade and usuario.distancia_maxima:
        # Aqui você implementaria a lógica de distância geográfica
        # Por enquanto, apenas filtrar por cidade
        usuarios = usuarios.filter(cidade__icontains=usuario.cidade)
    
    # Excluir usuários que já foram curtidos ou rejeitados
    relacionamentos_existentes = Relacionamento.objects.filter(
        remetente=usuario
    ).values_list('destinatario_id', flat=True)
    
    usuarios = usuarios.exclude(id__in=relacionamentos_existentes)
    
    return usuarios[:20]  # Limitar a 20 resultados
