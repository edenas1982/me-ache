from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Interface administrativa para o modelo Usuario"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_vip', 'is_verificado', 'is_active', 'data_criacao')
    list_filter = ('is_vip', 'is_verificado', 'is_active', 'genero', 'cidade', 'data_criacao')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'cidade')
    ordering = ('-data_criacao',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {
            'fields': ('first_name', 'last_name', 'email', 'data_nascimento', 'genero', 'bio', 'foto_perfil')
        }),
        ('Localização', {
            'fields': ('cidade', 'estado', 'latitude', 'longitude')
        }),
        ('Preferências', {
            'fields': ('genero_interesse', 'idade_minima', 'idade_maxima', 'distancia_maxima')
        }),
        ('Configurações de Privacidade', {
            'fields': ('mostrar_idade', 'mostrar_localizacao')
        }),
        ('Status da Conta', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_vip', 'is_verificado')
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'data_criacao', 'ultima_atividade')
        }),
        ('Permissões', {
            'fields': ('groups', 'user_permissions')
        }),
    )
    
    readonly_fields = ('data_criacao', 'ultima_atividade', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
