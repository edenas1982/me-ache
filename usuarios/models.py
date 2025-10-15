from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Usuario(AbstractUser):
    """Modelo personalizado de usuário para o Me Ache"""
    
    # Campos básicos do perfil
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biografia")
    foto_perfil = models.ImageField(upload_to='perfis/', null=True, blank=True, verbose_name="Foto de Perfil")
    
    # Localização
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, verbose_name="Estado")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Longitude")
    
    # Preferências de relacionamento
    GENERO_CHOICES = [
        ('H', 'Homem'),
        ('M', 'Mulher'),
        ('C_EL', 'Casal (Ele/Ela)'),
        ('C_EE', 'Casal (Ele/Ele)'),
        ('C_MM', 'Casal (Ela/Ela)'),
        ('T', 'Transexual'),
        ('CD', 'Crossdresser (CD)'),
        ('TV', 'Travesti'),
        ('GP_F', 'GP – Garota de Programa'),
        ('GP_M', 'GP – Garoto de Programa'),
    ]
    
    genero = models.CharField(max_length=4, choices=GENERO_CHOICES, blank=True, verbose_name="Gênero")
    
    GENERO_INTERESSE_CHOICES = [
        ('H', 'Homens'),
        ('M', 'Mulheres'),
        ('C_EL', 'Casais (Ele/Ela)'),
        ('C_EE', 'Casais (Ele/Ele)'),
        ('C_MM', 'Casais (Ela/Ela)'),
        ('T', 'Transexuais'),
        ('CD', 'Crossdressers'),
        ('TV', 'Travestis'),
        ('GP_F', 'GPs Femininas'),
        ('GP_M', 'GPs Masculinos'),
        ('TODOS', 'Todos'),
    ]
    
    genero_interesse = models.CharField(max_length=6, choices=GENERO_INTERESSE_CHOICES, blank=True, verbose_name="Interesse em")
    idade_minima = models.IntegerField(default=18, validators=[MinValueValidator(18), MaxValueValidator(100)], verbose_name="Idade Mínima")
    idade_maxima = models.IntegerField(default=50, validators=[MinValueValidator(18), MaxValueValidator(100)], verbose_name="Idade Máxima")
    distancia_maxima = models.IntegerField(default=50, validators=[MinValueValidator(1), MaxValueValidator(500)], verbose_name="Distância Máxima (km)")
    
    # Status da conta
    is_verificado = models.BooleanField(default=False, verbose_name="Conta Verificada")
    is_vip = models.BooleanField(default=False, verbose_name="Conta VIP")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    ultima_atividade = models.DateTimeField(auto_now=True, verbose_name="Última Atividade")
    
    # Configurações de privacidade
    mostrar_idade = models.BooleanField(default=True, verbose_name="Mostrar Idade")
    mostrar_localizacao = models.BooleanField(default=True, verbose_name="Mostrar Localização")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.username} - {self.get_full_name() or self.email}"
    
    @property
    def idade(self):
        """Calcula a idade do usuário"""
        if self.data_nascimento:
            from datetime import date
            today = date.today()
            return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return None
    
    @property
    def nome_completo(self):
        """Retorna o nome completo do usuário"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
