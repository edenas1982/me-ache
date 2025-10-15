from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria usuários de teste para o feed'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Lista de usuários de teste
            test_users = [
                {
                    'username': 'ana_silva',
                    'first_name': 'Ana',
                    'last_name': 'Silva',
                    'email': 'ana@teste.com',
                    'genero': 'Mulher',
                    'cidade': 'São Paulo',
                    'estado': 'SP',
                    'is_vip': True,
                    'is_verificado': True,
                },
                {
                    'username': 'bruno_santos',
                    'first_name': 'Bruno',
                    'last_name': 'Santos',
                    'email': 'bruno@teste.com',
                    'genero': 'Homem',
                    'cidade': 'Rio de Janeiro',
                    'estado': 'RJ',
                    'is_vip': False,
                    'is_verificado': False,
                },
                {
                    'username': 'carla_oliveira',
                    'first_name': 'Carla',
                    'last_name': 'Oliveira',
                    'email': 'carla@teste.com',
                    'genero': 'Mulher',
                    'cidade': 'Belo Horizonte',
                    'estado': 'MG',
                    'is_vip': True,
                    'is_verificado': True,
                },
                {
                    'username': 'diego_santos',
                    'first_name': 'Diego',
                    'last_name': 'Santos',
                    'email': 'diego@teste.com',
                    'genero': 'Homem',
                    'cidade': 'Salvador',
                    'estado': 'BA',
                    'is_vip': False,
                    'is_verificado': False,
                },
                {
                    'username': 'elena_ferreira',
                    'first_name': 'Elena',
                    'last_name': 'Ferreira',
                    'email': 'elena@teste.com',
                    'genero': 'Mulher',
                    'cidade': 'Fortaleza',
                    'estado': 'CE',
                    'is_vip': True,
                    'is_verificado': True,
                }
            ]
            
            created_count = 0
            for user_data in test_users:
                username = user_data['username']
                
                # Verificar se o usuário já existe
                if User.objects.filter(username=username).exists():
                    self.stdout.write(f'Usuário {username} já existe, pulando...')
                    continue
                
                # Criar usuário
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password='teste123',  # Senha padrão para todos
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    genero=user_data['genero'],
                    cidade=user_data['cidade'],
                    estado=user_data['estado'],
                    is_vip=user_data['is_vip'],
                    is_verificado=user_data['is_verificado'],
                )
                
                created_count += 1
                self.stdout.write(f'Usuário {username} criado com sucesso!')
            
            self.stdout.write(
                self.style.SUCCESS(f'Criados {created_count} usuários de teste!')
            )
            self.stdout.write('Senha padrão para todos: teste123')
