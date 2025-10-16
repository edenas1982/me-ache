from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from math import radians, cos, sin, asin, sqrt


class TipoRelacionamento(models.Model):
    """Modelo para tipos de relacionamento"""
    nome = models.CharField(max_length=50, unique=True, verbose_name="Tipo de Relacionamento")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")
    
    class Meta:
        verbose_name = "Tipo de Relacionamento"
        verbose_name_plural = "Tipos de Relacionamento"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class Signo(models.Model):
    """Modelo para signos zodiacais"""
    nome = models.CharField(max_length=20, unique=True, verbose_name="Signo")
    data_inicio = models.CharField(max_length=10, verbose_name="Data Início")
    data_fim = models.CharField(max_length=10, verbose_name="Data Fim")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    class Meta:
        verbose_name = "Signo"
        verbose_name_plural = "Signos"
        ordering = ['ordem']
    
    def __str__(self):
        return self.nome


class CorOlhos(models.Model):
    """Modelo para cores dos olhos"""
    nome = models.CharField(max_length=30, unique=True, verbose_name="Cor dos Olhos")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    class Meta:
        verbose_name = "Cor dos Olhos"
        verbose_name_plural = "Cores dos Olhos"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class CorCabelos(models.Model):
    """Modelo para cores dos cabelos"""
    nome = models.CharField(max_length=30, unique=True, verbose_name="Cor dos Cabelos")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    class Meta:
        verbose_name = "Cor dos Cabelos"
        verbose_name_plural = "Cores dos Cabelos"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class DadosPessoaisDetalhados(models.Model):
    """Modelo para dados pessoais detalhados de cada pessoa"""
    
    # Relacionamento com usuário
    usuario = models.ForeignKey(
        'Usuario', 
        on_delete=models.CASCADE, 
        related_name='dados_pessoais_detalhados',
        verbose_name="Usuário"
    )
    
    # Identificação da pessoa (para casais)
    PESSOA_CHOICES = [
        ('principal', 'Pessoa Principal'),
        ('parceiro', 'Parceiro(a)'),
    ]
    pessoa = models.CharField(
        max_length=10, 
        choices=PESSOA_CHOICES, 
        default='principal',
        verbose_name="Pessoa"
    )
    
    # Dados pessoais
    nome_apelido = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Nome / Apelido Público"
    )
    data_nascimento = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data de Nascimento"
    )
    signo = models.ForeignKey(
        'Signo', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Signo"
    )
    altura = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name="Altura (cm)"
    )
    peso = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name="Peso (kg)"
    )
    cor_olhos = models.ForeignKey(
        'CorOlhos', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Cor dos Olhos"
    )
    cor_cabelos = models.ForeignKey(
        'CorCabelos', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Cor dos Cabelos"
    )
    profissao_ocupacao = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Profissão / Ocupação"
    )
    cidade_atual = models.ForeignKey(
        'Cidade', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Cidade Atual",
        related_name='pessoas_cidade_atual'
    )
    origem = models.ForeignKey(
        'Cidade', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Origem (onde nasceu)",
        related_name='pessoas_origem'
    )
    
    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Dados Pessoais Detalhados"
        verbose_name_plural = "Dados Pessoais Detalhados"
        unique_together = ['usuario', 'pessoa']
        ordering = ['usuario', 'pessoa']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_pessoa_display()}"
    
    @property
    def idade(self):
        """Calcula a idade baseada na data de nascimento"""
        if self.data_nascimento:
            from datetime import date
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None


class EstiloVida(models.Model):
    """Modelo para estilo de vida de cada pessoa"""
    
    # Relacionamento com usuário
    usuario = models.ForeignKey(
        'Usuario', 
        on_delete=models.CASCADE, 
        related_name='estilos_vida',
        verbose_name="Usuário"
    )
    
    # Identificação da pessoa (para casais)
    PESSOA_CHOICES = [
        ('principal', 'Pessoa Principal'),
        ('parceiro', 'Parceiro(a)'),
    ]
    pessoa = models.CharField(
        max_length=10, 
        choices=PESSOA_CHOICES, 
        default='principal',
        verbose_name="Pessoa"
    )
    
    # Opções para campos de estilo de vida
    FUMANTE_CHOICES = [
        ('nao', 'Não'),
        ('sim', 'Sim'),
        ('ocasionalmente', 'Ocasionalmente'),
    ]
    
    BEBE_CHOICES = [
        ('nao', 'Não'),
        ('sim', 'Sim'),
        ('socialmente', 'Socialmente'),
    ]
    
    ESPORTES_CHOICES = [
        ('nao', 'Não'),
        ('sim', 'Sim'),
        ('as_vezes', 'Às vezes'),
    ]
    
    FILHOS_CHOICES = [
        ('nao', 'Não'),
        ('sim', 'Sim'),
        ('adultos', 'Adultos'),
        ('mora_com_filhos', 'Mora com filhos'),
    ]
    
    TATUAGENS_CHOICES = [
        ('nao', 'Não'),
        ('sim', 'Sim'),
        ('varios', 'Vários'),
    ]
    
    # Campos de estilo de vida
    fumante = models.CharField(
        max_length=15, 
        choices=FUMANTE_CHOICES, 
        default='nao',
        verbose_name="Fumante"
    )
    bebe = models.CharField(
        max_length=15, 
        choices=BEBE_CHOICES, 
        default='nao',
        verbose_name="Bebe"
    )
    pratica_esportes = models.CharField(
        max_length=15, 
        choices=ESPORTES_CHOICES, 
        default='nao',
        verbose_name="Pratica Esportes"
    )
    tem_filhos = models.CharField(
        max_length=20, 
        choices=FILHOS_CHOICES, 
        default='nao',
        verbose_name="Tem Filhos?"
    )
    tatuagens_piercings = models.CharField(
        max_length=15, 
        choices=TATUAGENS_CHOICES, 
        default='nao',
        verbose_name="Possui Tatuagens ou Piercings?"
    )
    
    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Estilo de Vida"
        verbose_name_plural = "Estilos de Vida"
        unique_together = ['usuario', 'pessoa']
        ordering = ['usuario', 'pessoa']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_pessoa_display()}"


class IdentidadePreferencias(models.Model):
    """Modelo para identidade e preferências de cada pessoa"""
    
    # Relacionamento com usuário
    usuario = models.ForeignKey(
        'Usuario', 
        on_delete=models.CASCADE, 
        related_name='identidades_preferencias',
        verbose_name="Usuário"
    )
    
    # Identificação da pessoa (para casais)
    PESSOA_CHOICES = [
        ('principal', 'Pessoa Principal'),
        ('parceiro', 'Parceiro(a)'),
    ]
    pessoa = models.CharField(
        max_length=10, 
        choices=PESSOA_CHOICES, 
        default='principal',
        verbose_name="Pessoa"
    )
    
    # Opções para campos de identidade
    GENERO_CHOICES = [
        ('homem', 'Homem'),
        ('mulher', 'Mulher'),
        ('trans', 'Trans'),
        ('outro', 'Outro'),
    ]
    
    ORIENTACAO_CHOICES = [
        ('hetero', 'Hetero'),
        ('homo', 'Homo'),
        ('bi', 'Bi'),
        ('pan', 'Pan'),
        ('outro', 'Outro'),
    ]
    
    CONTATOS_CHOICES = [
        ('homens', 'Homens'),
        ('mulheres', 'Mulheres'),
        ('casais', 'Casais'),
        ('todos', 'Todos'),
    ]
    
    # Campos de identidade e preferências
    genero = models.CharField(
        max_length=10, 
        choices=GENERO_CHOICES, 
        blank=True,
        verbose_name="Gênero"
    )
    orientacao_sexual = models.CharField(
        max_length=10, 
        choices=ORIENTACAO_CHOICES, 
        blank=True,
        verbose_name="Orientação Sexual"
    )
    aberto_contatos_com = models.CharField(
        max_length=10, 
        choices=CONTATOS_CHOICES, 
        blank=True,
        verbose_name="Aberto a novos contatos com"
    )
    
    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Identidade e Preferências"
        verbose_name_plural = "Identidades e Preferências"
        unique_together = ['usuario', 'pessoa']
        ordering = ['usuario', 'pessoa']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_pessoa_display()}"


class ConfiguracoesPrivacidade(models.Model):
    """Modelo para configurações de privacidade"""
    
    # Relacionamento com usuário
    usuario = models.OneToOneField(
        'Usuario', 
        on_delete=models.CASCADE, 
        related_name='configuracoes_privacidade',
        verbose_name="Usuário"
    )
    
    # Configurações de privacidade
    mostrar_idade = models.BooleanField(default=True, verbose_name="Mostrar Idade")
    mostrar_cidade = models.BooleanField(default=True, verbose_name="Mostrar Cidade")
    
    MENSAGENS_CHOICES = [
        ('todos', 'Todos'),
        ('vips', 'Somente VIPs'),
        ('seguidores', 'Seguidores'),
    ]
    disponivel_mensagens = models.CharField(
        max_length=15, 
        choices=MENSAGENS_CHOICES, 
        default='todos',
        verbose_name="Disponível para Mensagens"
    )
    
    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Configurações de Privacidade"
        verbose_name_plural = "Configurações de Privacidade"
    
    def __str__(self):
        return f"Privacidade - {self.usuario.username}"


class Usuario(AbstractUser):
    """Modelo personalizado de usuário para o Me Ache"""
    
    # Campos básicos do perfil
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    bio = models.TextField(max_length=1000, blank=True, verbose_name="Biografia")
    foto_perfil = models.ImageField(upload_to='perfis/', null=True, blank=True, verbose_name="Foto de Perfil")
    
    # Localização
    cidade = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, verbose_name="Estado")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Longitude")
    
    # Nova localização usando tabela Cidade
    cidade_ref = models.ForeignKey(
        'Cidade', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Cidade de Referência",
        related_name='usuarios'
    )
    
    # Opções de perfil unificadas com separadores
    PERFIL_CHOICES = [
        # Separador - Perfil Individual
        ('', '─── PERFIL INDIVIDUAL ───'),
        ('individual_homem', 'Homem'),
        ('individual_mulher', 'Mulher'),
        ('individual_transexual', 'Transexual'),
        ('individual_crossdresser', 'Crossdresser (CD)'),
        ('individual_travesti', 'Travesti'),
        ('individual_gp_feminina', 'GP Feminina'),
        ('individual_gp_masculina', 'GP Masculina'),
        
        # Separador - Perfil Casal
        ('', '─── PERFIL CASAL ───'),
        ('casal_ele_ela', 'Casal (Ele/Ela)'),
        ('casal_ela_ela', 'Casal (Ela/Ela)'),
        ('casal_ele_ele', 'Casal (Ele/Ele)'),
    ]
    
    tipo_perfil = models.CharField(
        max_length=25, 
        choices=PERFIL_CHOICES, 
        default='individual_homem',
        verbose_name="Tipo de Perfil"
    )
    
    # Manter gênero para compatibilidade (será preenchido automaticamente)
    GENERO_CHOICES = [
        ('H', 'Homem'),
        ('M', 'Mulher'),
        ('T', 'Transexual'),
        ('CD', 'Crossdresser (CD)'),
        ('TV', 'Travesti'),
        ('GP_F', 'GP Feminina'),
        ('GP_M', 'GP Masculina'),
    ]
    
    genero = models.CharField(max_length=4, choices=GENERO_CHOICES, blank=True, verbose_name="Gênero")
    
    # Campos para parceiro (modo casal)
    first_name_parceiro = models.CharField(max_length=30, blank=True, verbose_name="Nome do Parceiro")
    last_name_parceiro = models.CharField(max_length=30, blank=True, verbose_name="Sobrenome do Parceiro")
    data_nascimento_parceiro = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento do Parceiro")
    genero_parceiro = models.CharField(max_length=4, choices=GENERO_CHOICES, blank=True, verbose_name="Gênero do Parceiro")
    foto_perfil_parceiro = models.ImageField(upload_to='perfis/parceiros/', null=True, blank=True, verbose_name="Foto do Parceiro")
    
    # Informações pessoais adicionais
    profissao = models.CharField(max_length=100, blank=True, verbose_name="Profissão")
    estado_civil = models.CharField(max_length=50, blank=True, verbose_name="Estado Civil")
    orientacao_sexual = models.CharField(max_length=50, blank=True, verbose_name="Orientação Sexual")
    
    # Profissão e estado civil do parceiro
    profissao_parceiro = models.CharField(max_length=100, blank=True, verbose_name="Profissão do Parceiro")
    estado_civil_parceiro = models.CharField(max_length=50, blank=True, verbose_name="Estado Civil do Parceiro")
    orientacao_sexual_parceiro = models.CharField(max_length=50, blank=True, verbose_name="Orientação Sexual do Parceiro")
    
    # Campos de relacionamento (para casais)
    tipo_relacionamento = models.ForeignKey(
        'TipoRelacionamento', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Tipo de Relacionamento",
        related_name='usuarios'
    )
    tempo_juntos = models.CharField(max_length=50, blank=True, verbose_name="Tempo Juntos")
    
    # Preferências de relacionamento
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
    
    @property
    def nome_completo_parceiro(self):
        """Retorna o nome completo do parceiro"""
        return f"{self.first_name_parceiro} {self.last_name_parceiro}".strip()
    
    @property
    def idade_parceiro(self):
        """Calcula a idade do parceiro"""
        if self.data_nascimento_parceiro:
            from datetime import date
            today = date.today()
            return today.year - self.data_nascimento_parceiro.year - ((today.month, today.day) < (self.data_nascimento_parceiro.month, self.data_nascimento_parceiro.day))
        return None
    
    @property
    def is_casal(self):
        """Verifica se é um perfil de casal"""
        return self.tipo_perfil != 'individual'
    
    @property
    def progresso_perfil(self):
        """Calcula o progresso de preenchimento do perfil"""
        campos_obrigatorios = [
            self.first_name, self.last_name, self.email, 
            self.data_nascimento, self.genero, self.bio, 
            self.cidade, self.estado
        ]
        
        if self.is_casal:
            campos_obrigatorios.extend([
                self.first_name_parceiro, self.last_name_parceiro,
                self.data_nascimento_parceiro, self.genero_parceiro
            ])
        
        campos_preenchidos = sum(1 for campo in campos_obrigatorios if campo)
        total_campos = len(campos_obrigatorios)
        
        return int((campos_preenchidos / total_campos) * 100)
    
    def distancia_para_usuario(self, outro_usuario):
        """Calcula distância para outro usuário em quilômetros"""
        # Priorizar cidade_ref se disponível
        if self.cidade_ref and outro_usuario.cidade_ref:
            return self.cidade_ref.distancia_para(outro_usuario.cidade_ref)
        
        # Fallback para coordenadas diretas
        if (self.latitude and self.longitude and 
            outro_usuario.latitude and outro_usuario.longitude):
            return Cidade.calcular_distancia_haversine(
                float(self.latitude), float(self.longitude),
                float(outro_usuario.latitude), float(outro_usuario.longitude)
            )
        
        return None
    
    def usuarios_proximos(self, raio_km=50, genero_interesse=None):
        """Busca usuários próximos dentro de um raio específico"""
        if not self.cidade_ref:
            return Usuario.objects.none()
        
        # Buscar usuários com cidade_ref
        usuarios_proximos = Usuario.objects.filter(
            cidade_ref__isnull=False
        ).exclude(id=self.id)
        
        # Filtrar por gênero de interesse se especificado
        if genero_interesse:
            usuarios_proximos = usuarios_proximos.filter(
                genero_interesse=genero_interesse
            )
        
        # Calcular distância para cada usuário
        usuarios_com_distancia = []
        for usuario in usuarios_proximos:
            distancia = self.distancia_para_usuario(usuario)
            if distancia and distancia <= raio_km:
                usuarios_com_distancia.append((usuario, distancia))
        
        # Ordenar por distância
        usuarios_com_distancia.sort(key=lambda x: x[1])
        
        return usuarios_com_distancia


class Interesse(models.Model):
    """Modelo para interesses/procurando por"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Interesse"
        verbose_name_plural = "Interesses"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class Objetivo(models.Model):
    """Modelo para objetivos de relacionamento"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Objetivo"
        verbose_name_plural = "Objetivos"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class Fetiche(models.Model):
    """Modelo para fetiches/preferências"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Fetiche"
        verbose_name_plural = "Fetiches"
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class UsuarioInteresse(models.Model):
    """Relacionamento muitos-para-muitos entre usuário e interesses"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='interesses_usuario')
    interesse = models.ForeignKey(Interesse, on_delete=models.CASCADE)
    data_adicao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'interesse']
        verbose_name = "Interesse do Usuário"
        verbose_name_plural = "Interesses dos Usuários"


class UsuarioObjetivo(models.Model):
    """Relacionamento muitos-para-muitos entre usuário e objetivos"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='objetivos_usuario')
    objetivo = models.ForeignKey(Objetivo, on_delete=models.CASCADE)
    data_adicao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'objetivo']
        verbose_name = "Objetivo do Usuário"
        verbose_name_plural = "Objetivos dos Usuários"


class UsuarioFetiche(models.Model):
    """Relacionamento muitos-para-muitos entre usuário e fetiches"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='fetiches_usuario')
    fetiche = models.ForeignKey(Fetiche, on_delete=models.CASCADE)
    data_adicao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'fetiche']
        verbose_name = "Fetiche do Usuário"
        verbose_name_plural = "Fetiches dos Usuários"


class Cidade(models.Model):
    """Modelo para armazenar cidades brasileiras com coordenadas"""
    
    nome = models.CharField(max_length=100, verbose_name="Nome da Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado (UF)")
    codigo_ibge = models.CharField(max_length=7, unique=True, verbose_name="Código IBGE")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude")
    populacao = models.IntegerField(null=True, blank=True, verbose_name="População")
    ativa = models.BooleanField(default=True, verbose_name="Cidade Ativa")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        unique_together = ['nome', 'estado']
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
        ordering = ['estado', 'nome']
    
    def __str__(self):
        return f"{self.nome}/{self.estado}"
    
    @property
    def nome_completo(self):
        """Retorna nome da cidade com estado"""
        return f"{self.nome}, {self.estado}"
    
    @staticmethod
    def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
        """
        Calcula a distância entre dois pontos usando a fórmula de Haversine
        Retorna a distância em quilômetros
        """
        # Converter graus para radianos
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Raio da Terra em quilômetros
        r = 6371
        
        return round(c * r, 2)
    
    def distancia_para(self, outra_cidade):
        """Calcula distância para outra cidade"""
        return self.calcular_distancia_haversine(
            float(self.latitude), float(self.longitude),
            float(outra_cidade.latitude), float(outra_cidade.longitude)
        )
    
    @classmethod
    def buscar_por_nome(cls, nome, estado=None):
        """Busca cidades por nome, opcionalmente filtrando por estado"""
        queryset = cls.objects.filter(nome__icontains=nome, ativa=True)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset.order_by('nome')


