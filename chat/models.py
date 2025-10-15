from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class Conversa(models.Model):
    """Modelo para conversas entre usuários"""
    
    participantes = models.ManyToManyField(Usuario, related_name='conversas', verbose_name="Participantes")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    is_ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Conversa"
        verbose_name_plural = "Conversas"
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        participantes = ", ".join([p.username for p in self.participantes.all()])
        return f"Conversa: {participantes}"
    
    @property
    def ultima_mensagem(self):
        return self.mensagens.filter(is_ativo=True).last()


class Mensagem(models.Model):
    """Modelo para mensagens no chat"""
    
    TIPO_CHOICES = [
        ('texto', 'Texto'),
        ('imagem', 'Imagem'),
        ('video', 'Vídeo'),
        ('audio', 'Áudio'),
        ('arquivo', 'Arquivo'),
    ]
    
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens', verbose_name="Conversa")
    remetente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_enviadas', verbose_name="Remetente")
    conteudo = models.TextField(verbose_name="Conteúdo")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='texto', verbose_name="Tipo")
    arquivo = models.FileField(upload_to='chat/arquivos/', null=True, blank=True, verbose_name="Arquivo")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    is_ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Status da mensagem
    is_lida = models.BooleanField(default=False, verbose_name="Lida")
    data_leitura = models.DateTimeField(null=True, blank=True, verbose_name="Data de Leitura")
    
    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['data_criacao']
    
    def __str__(self):
        return f"{self.remetente.username}: {self.conteudo[:50]}..."


class Notificacao(models.Model):
    """Modelo para notificações do sistema"""
    
    TIPO_CHOICES = [
        ('like', 'Curtida'),
        ('match', 'Match'),
        ('mensagem', 'Nova Mensagem'),
        ('comentario', 'Novo Comentário'),
        ('sistema', 'Sistema'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificacoes', verbose_name="Usuário")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    conteudo = models.TextField(verbose_name="Conteúdo")
    url = models.URLField(blank=True, verbose_name="URL")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    is_lida = models.BooleanField(default=False, verbose_name="Lida")
    data_leitura = models.DateTimeField(null=True, blank=True, verbose_name="Data de Leitura")
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"
