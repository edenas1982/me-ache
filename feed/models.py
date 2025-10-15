from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

Usuario = get_user_model()


class Postagem(models.Model):
    """Modelo para postagens no feed"""
    
    TIPO_CHOICES = [
        ('texto', 'Texto'),
        ('imagem', 'Imagem'),
        ('video', 'Vídeo'),
        ('localizacao', 'Localização'),
    ]
    
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='postagens', verbose_name="Autor")
    conteudo = models.TextField(verbose_name="Conteúdo")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='texto', verbose_name="Tipo")
    imagem = models.ImageField(upload_to='postagens/imagens/', null=True, blank=True, verbose_name="Imagem")
    video = models.FileField(
        upload_to='postagens/videos/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'wmv'])],
        verbose_name="Vídeo"
    )
    localizacao = models.CharField(max_length=200, blank=True, verbose_name="Localização")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Longitude")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    is_ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Interações
    curtidas = models.ManyToManyField(Usuario, through='Curtida', related_name='postagens_curtidas', blank=True)
    visualizacoes = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    
    class Meta:
        verbose_name = "Postagem"
        verbose_name_plural = "Postagens"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.autor.username} - {self.conteudo[:50]}..."
    
    @property
    def total_curtidas(self):
        return self.curtidas.count()
    
    @property
    def total_comentarios(self):
        return self.comentarios.count()


class Curtida(models.Model):
    """Modelo para curtidas em postagens"""
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuário")
    postagem = models.ForeignKey(Postagem, on_delete=models.CASCADE, verbose_name="Postagem")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Curtida"
        verbose_name_plural = "Curtidas"
        unique_together = ['usuario', 'postagem']
    
    def __str__(self):
        return f"{self.usuario.username} curtiu {self.postagem.id}"


class Comentario(models.Model):
    """Modelo para comentários em postagens"""
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comentarios', verbose_name="Usuário")
    postagem = models.ForeignKey(Postagem, on_delete=models.CASCADE, related_name='comentarios', verbose_name="Postagem")
    conteudo = models.TextField(verbose_name="Conteúdo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    is_ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ['data_criacao']
    
    def __str__(self):
        return f"{self.usuario.username} comentou em {self.postagem.id}"


class Relacionamento(models.Model):
    """Modelo para relacionamentos entre usuários (match, like, dislike)"""
    
    TIPO_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('match', 'Match'),
        ('super_like', 'Super Like'),
    ]
    
    remetente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='relacionamentos_enviados', verbose_name="Remetente")
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='relacionamentos_recebidos', verbose_name="Destinatário")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    is_ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Relacionamento"
        verbose_name_plural = "Relacionamentos"
        unique_together = ['remetente', 'destinatario']
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.remetente.username} {self.get_tipo_display()} {self.destinatario.username}"
