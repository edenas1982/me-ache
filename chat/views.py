from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Conversa, Mensagem, Notificacao


@login_required
def lista_conversas(request):
    """Lista todas as conversas do usuário"""
    conversas = Conversa.objects.filter(participantes=request.user).order_by('-data_atualizacao')
    
    context = {
        'conversas': conversas,
    }
    
    return render(request, 'chat/lista.html', context)


@login_required
def detalhes_conversa(request, conversa_id):
    """Detalhes de uma conversa específica"""
    conversa = get_object_or_404(Conversa, id=conversa_id, participantes=request.user)
    mensagens = conversa.mensagens.filter(is_ativo=True).order_by('data_criacao')
    
    # Marcar mensagens como lidas
    mensagens.filter(remetente__ne=request.user).update(is_lida=True)
    
    context = {
        'conversa': conversa,
        'mensagens': mensagens,
    }
    
    return render(request, 'chat/detalhes.html', context)


@login_required
@require_http_methods(["POST"])
def enviar_mensagem(request, conversa_id):
    """Enviar mensagem via AJAX"""
    conversa = get_object_or_404(Conversa, id=conversa_id, participantes=request.user)
    
    try:
        conteudo = request.POST.get('conteudo', '').strip()
        if not conteudo:
            return JsonResponse({
                'success': False,
                'error': 'Mensagem não pode estar vazia'
            })
        
        mensagem = Mensagem.objects.create(
            conversa=conversa,
            remetente=request.user,
            conteudo=conteudo
        )
        
        # Atualizar data de atualização da conversa
        conversa.save()
        
        return JsonResponse({
            'success': True,
            'mensagem': {
                'id': mensagem.id,
                'conteudo': mensagem.conteudo,
                'remetente': mensagem.remetente.username,
                'data_criacao': mensagem.data_criacao.strftime('%d/%m/%Y %H:%M')
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def iniciar_conversa(request, user_id):
    """Iniciar conversa com outro usuário"""
    from usuarios.models import Usuario
    
    destinatario = get_object_or_404(Usuario, id=user_id)
    
    # Verificar se já existe conversa
    conversa_existente = Conversa.objects.filter(
        participantes=request.user
    ).filter(
        participantes=destinatario
    ).first()
    
    if conversa_existente:
        return redirect('chat:detalhes', conversa_id=conversa_existente.id)
    
    # Criar nova conversa
    conversa = Conversa.objects.create()
    conversa.participantes.add(request.user, destinatario)
    
    return redirect('chat:detalhes', conversa_id=conversa.id)
