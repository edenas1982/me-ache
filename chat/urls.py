from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.lista_conversas, name='lista'),
    path('conversa/<int:conversa_id>/', views.detalhes_conversa, name='detalhes'),
    path('conversa/<int:conversa_id>/enviar/', views.enviar_mensagem, name='enviar'),
    path('iniciar/<int:user_id>/', views.iniciar_conversa, name='iniciar'),
]
