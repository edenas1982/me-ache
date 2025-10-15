from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Landing page
    path('', views.landing, name='landing'),
    
    # Autenticação
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.UsuarioRegistrationView.as_view(), name='cadastro'),
    
    # Perfil
    path('perfil/', views.PerfilDetailView.as_view(), name='perfil'),
    path('perfil/editar/', views.PerfilUpdateView.as_view(), name='editar_perfil'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    
    # Upload de foto
    path('upload-foto/', views.upload_foto_perfil, name='upload_foto'),
    
    # Busca e visualização de usuários
    path('buscar/', views.buscar_usuarios, name='buscar'),
    path('perfil/<int:user_id>/', views.ver_perfil_usuario, name='ver_perfil'),
    
    # Fluxo de cadastro guiado
    path('cadastro-genero/', views.cadastro_genero, name='cadastro_genero'),
    path('cadastro-interesses/', views.cadastro_interesses, name='cadastro_interesses'),
    path('cadastro-username/', views.cadastro_username, name='cadastro_username'),
    path('cadastro-localizacao/', views.cadastro_localizacao, name='cadastro_localizacao'),
    path('cadastro-login/', views.cadastro_login, name='cadastro_login'),
    path('cadastro-foto/', views.cadastro_foto, name='cadastro_foto'),
    path('validar-username/', views.validar_username, name='validar_username'),
    
    # Perfil visitante
    path('perfil/<str:username>/', views.perfil_visitante, name='perfil_visitante'),
]
