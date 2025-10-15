from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

Usuario = get_user_model()


class PlanoAssinatura(models.Model):
    """Modelo para planos de assinatura VIP"""
    
    nome = models.CharField(max_length=100, verbose_name="Nome do Plano")
    descricao = models.TextField(verbose_name="Descrição")
    preco_mensal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Mensal")
    preco_anual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço Anual")
    
    # Recursos incluídos
    likes_ilimitados = models.BooleanField(default=False, verbose_name="Likes Ilimitados")
    super_likes_diarios = models.IntegerField(default=0, verbose_name="Super Likes Diários")
    boost_perfil = models.BooleanField(default=False, verbose_name="Boost de Perfil")
    filtros_avancados = models.BooleanField(default=False, verbose_name="Filtros Avançados")
    ver_quem_curtiu = models.BooleanField(default=False, verbose_name="Ver Quem Curtiu")
    desfazer_ultimo_like = models.BooleanField(default=False, verbose_name="Desfazer Último Like")
    
    # Configurações
    is_ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.IntegerField(default=0, verbose_name="Ordem")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Plano de Assinatura"
        verbose_name_plural = "Planos de Assinatura"
        ordering = ['ordem', 'preco_mensal']
    
    def __str__(self):
        return self.nome


class Assinatura(models.Model):
    """Modelo para assinaturas dos usuários"""
    
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
        ('suspensa', 'Suspensa'),
    ]
    
    TIPO_CHOICES = [
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='assinaturas', verbose_name="Usuário")
    plano = models.ForeignKey(PlanoAssinatura, on_delete=models.CASCADE, verbose_name="Plano")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa', verbose_name="Status")
    
    # Datas
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(verbose_name="Data de Fim")
    data_cancelamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Cancelamento")
    
    # Pagamento
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago")
    metodo_pagamento = models.CharField(max_length=50, blank=True, verbose_name="Método de Pagamento")
    transacao_id = models.CharField(max_length=200, blank=True, verbose_name="ID da Transação")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.plano.nome}"
    
    @property
    def is_ativa(self):
        from django.utils import timezone
        return self.status == 'ativa' and self.data_fim > timezone.now()


class Pagamento(models.Model):
    """Modelo para histórico de pagamentos"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_CHOICES = [
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('boleto', 'Boleto'),
    ]
    
    assinatura = models.ForeignKey(Assinatura, on_delete=models.CASCADE, related_name='pagamentos', verbose_name="Assinatura")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES, verbose_name="Método")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    
    # Dados da transação
    transacao_id = models.CharField(max_length=200, unique=True, verbose_name="ID da Transação")
    gateway_pagamento = models.CharField(max_length=50, verbose_name="Gateway de Pagamento")
    dados_transacao = models.JSONField(null=True, blank=True, verbose_name="Dados da Transação")
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_processamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Processamento")
    
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Pagamento {self.transacao_id} - {self.get_status_display()}"
