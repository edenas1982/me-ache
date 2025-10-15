from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.home, name='home'),
    path('explorar/', views.explorar, name='explorar'),
    path('criar/', views.criar_postagem, name='criar_postagem'),
    path('postagem/<int:post_id>/', views.detalhes_postagem, name='detalhes_postagem'),
    path('postagem/<int:post_id>/curtir/', views.curtir_postagem, name='curtir_postagem'),
    path('postagem/<int:post_id>/comentar/', views.comentar_postagem, name='comentar_postagem'),
]
