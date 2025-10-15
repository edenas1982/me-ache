from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import PlanoAssinatura, Assinatura, Pagamento


@login_required
def planos(request):
    """Lista de planos de assinatura"""
    planos = PlanoAssinatura.objects.filter(is_ativo=True).order_by('ordem', 'preco_mensal')
    
    context = {
        'planos': planos,
    }
    
    return render(request, 'assinaturas/planos.html', context)


@login_required
def assinar_plano(request, plano_id):
    """Assinar um plano específico"""
    plano = get_object_or_404(PlanoAssinatura, id=plano_id, is_ativo=True)
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'mensal')
        
        # Criar assinatura
        from django.utils import timezone
        from datetime import timedelta
        
        data_inicio = timezone.now()
        if tipo == 'anual':
            data_fim = data_inicio + timedelta(days=365)
            valor = plano.preco_anual or plano.preco_mensal * 12
        else:
            data_fim = data_inicio + timedelta(days=30)
            valor = plano.preco_mensal
        
        assinatura = Assinatura.objects.create(
            usuario=request.user,
            plano=plano,
            tipo=tipo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            valor_pago=valor
        )
        
        # Redirecionar para pagamento
        return redirect('assinaturas:pagamento', assinatura_id=assinatura.id)
    
    context = {
        'plano': plano,
    }
    
    return render(request, 'assinaturas/assinar.html', context)


@login_required
def processar_pagamento(request, assinatura_id):
    """Processar pagamento da assinatura"""
    assinatura = get_object_or_404(Assinatura, id=assinatura_id, usuario=request.user)
    
    if request.method == 'POST':
        metodo = request.POST.get('metodo', 'pix')
        
        # Simular processamento de pagamento
        pagamento = Pagamento.objects.create(
            assinatura=assinatura,
            valor=assinatura.valor_pago,
            metodo=metodo,
            transacao_id=f"TXN_{assinatura.id}_{timezone.now().timestamp()}",
            gateway_pagamento='simulado',
            status='aprovado'
        )
        
        # Ativar assinatura
        assinatura.status = 'ativa'
        assinatura.metodo_pagamento = metodo
        assinatura.transacao_id = pagamento.transacao_id
        assinatura.save()
        
        # Ativar VIP no usuário
        request.user.is_vip = True
        request.user.save()
        
        messages.success(request, 'Assinatura ativada com sucesso!')
        return redirect('assinaturas:historico')
    
    context = {
        'assinatura': assinatura,
    }
    
    return render(request, 'assinaturas/pagamento.html', context)


@login_required
def cancelar_assinatura(request, assinatura_id):
    """Cancelar assinatura"""
    assinatura = get_object_or_404(Assinatura, id=assinatura_id, usuario=request.user)
    
    if request.method == 'POST':
        from django.utils import timezone
        
        assinatura.status = 'cancelada'
        assinatura.data_cancelamento = timezone.now()
        assinatura.save()
        
        # Desativar VIP no usuário
        request.user.is_vip = False
        request.user.save()
        
        messages.success(request, 'Assinatura cancelada com sucesso!')
        return redirect('assinaturas:historico')
    
    context = {
        'assinatura': assinatura,
    }
    
    return render(request, 'assinaturas/cancelar.html', context)


@login_required
def historico(request):
    """Histórico de assinaturas do usuário"""
    assinaturas = Assinatura.objects.filter(usuario=request.user).order_by('-data_criacao')
    
    context = {
        'assinaturas': assinaturas,
    }
    
    return render(request, 'assinaturas/historico.html', context)
