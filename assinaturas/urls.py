from django.urls import path
from . import views

app_name = 'assinaturas'

urlpatterns = [
    path('planos/', views.planos, name='planos'),
    path('assinar/<int:plano_id>/', views.assinar_plano, name='assinar'),
    path('pagamento/<int:assinatura_id>/', views.processar_pagamento, name='pagamento'),
    path('cancelar/<int:assinatura_id>/', views.cancelar_assinatura, name='cancelar'),
    path('historico/', views.historico, name='historico'),
]
