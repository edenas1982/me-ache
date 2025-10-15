from django.contrib import admin
from .models import Postagem, Curtida, Comentario, Relacionamento


@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin):
    list_display = ('autor', 'tipo', 'conteudo_preview', 'total_curtidas', 'total_comentarios', 'data_criacao', 'is_ativo')
    list_filter = ('tipo', 'is_ativo', 'data_criacao')
    search_fields = ('autor__username', 'conteudo', 'localizacao')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'visualizacoes')
    
    def conteudo_preview(self, obj):
        return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
    conteudo_preview.short_description = 'Conteúdo'


@admin.register(Curtida)
class CurtidaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'postagem', 'data_criacao')
    list_filter = ('data_criacao',)
    search_fields = ('usuario__username', 'postagem__conteudo')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'postagem', 'conteudo_preview', 'data_criacao', 'is_ativo')
    list_filter = ('is_ativo', 'data_criacao')
    search_fields = ('usuario__username', 'conteudo', 'postagem__conteudo')
    
    def conteudo_preview(self, obj):
        return obj.conteudo[:30] + '...' if len(obj.conteudo) > 30 else obj.conteudo
    conteudo_preview.short_description = 'Comentário'


@admin.register(Relacionamento)
class RelacionamentoAdmin(admin.ModelAdmin):
    list_display = ('remetente', 'destinatario', 'tipo', 'data_criacao', 'is_ativo')
    list_filter = ('tipo', 'is_ativo', 'data_criacao')
    search_fields = ('remetente__username', 'destinatario__username')
