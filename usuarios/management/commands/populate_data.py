from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random

from assinaturas.models import PlanoAssinatura, Assinatura
from feed.models import Postagem, Curtida, Comentario, Relacionamento
from chat.models import Conversa, Mensagem

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Número de usuários para criar'
        )

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população do banco de dados...')
        
        # Criar planos de assinatura
        self.criar_planos()
        
        # Criar usuários
        self.criar_usuarios(options['users'])
        
        # Criar postagens
        self.criar_postagens()
        
        # Criar relacionamentos
        self.criar_relacionamentos()
        
        # Criar conversas
        self.criar_conversas()
        
        self.stdout.write(
            self.style.SUCCESS('Dados de exemplo criados com sucesso!')
        )

    def criar_planos(self):
        """Criar planos de assinatura"""
        if not PlanoAssinatura.objects.exists():
            planos = [
                {
                    'nome': 'Básico',
                    'descricao': 'Perfeito para começar sua jornada no Me Ache',
                    'preco_mensal': 19.90,
                    'preco_anual': 199.90,
                    'likes_ilimitados': False,
                    'super_likes_diarios': 5,
                    'boost_perfil': False,
                    'filtros_avancados': True,
                    'ver_quem_curtiu': False,
                    'desfazer_ultimo_like': False,
                    'ordem': 1
                },
                {
                    'nome': 'Premium',
                    'descricao': 'Recursos avançados para encontrar sua pessoa especial',
                    'preco_mensal': 39.90,
                    'preco_anual': 399.90,
                    'likes_ilimitados': True,
                    'super_likes_diarios': 10,
                    'boost_perfil': True,
                    'filtros_avancados': True,
                    'ver_quem_curtiu': True,
                    'desfazer_ultimo_like': True,
                    'ordem': 2
                },
                {
                    'nome': 'VIP',
                    'descricao': 'Acesso total a todos os recursos exclusivos',
                    'preco_mensal': 79.90,
                    'preco_anual': 799.90,
                    'likes_ilimitados': True,
                    'super_likes_diarios': 20,
                    'boost_perfil': True,
                    'filtros_avancados': True,
                    'ver_quem_curtiu': True,
                    'desfazer_ultimo_like': True,
                    'ordem': 3
                }
            ]
            
            for plano_data in planos:
                PlanoAssinatura.objects.create(**plano_data)
            
            self.stdout.write('Planos de assinatura criados')

    def criar_usuarios(self, num_usuarios):
        """Criar usuários de exemplo"""
        nomes = [
            'Ana', 'Bruno', 'Carla', 'Diego', 'Elena', 'Felipe', 'Gabriela', 'Henrique',
            'Isabela', 'João', 'Karina', 'Lucas', 'Mariana', 'Nicolas', 'Olivia', 'Pedro',
            'Rafaela', 'Samuel', 'Tatiana', 'Vitor', 'Wendy', 'Xavier', 'Yasmin', 'Zeca'
        ]
        
        sobrenomes = [
            'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves',
            'Pereira', 'Lima', 'Gomes', 'Costa', 'Ribeiro', 'Martins', 'Carvalho',
            'Almeida', 'Lopes', 'Soares', 'Fernandes', 'Vieira', 'Barbosa'
        ]
        
        cidades = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Brasília',
            'Fortaleza', 'Manaus', 'Curitiba', 'Recife', 'Porto Alegre', 'Belém',
            'Goiânia', 'Guarulhos', 'Campinas', 'São Luís', 'São Gonçalo'
        ]
        
        estados = ['SP', 'RJ', 'MG', 'BA', 'DF', 'CE', 'AM', 'PR', 'PE', 'RS', 'PA', 'GO']
        
        generos = ['M', 'F', 'O']
        generos_interesse = ['M', 'F', 'A', 'O']
        
        bios = [
            'Adoro viajar e conhecer novas culturas!',
            'Apaixonado por música e arte.',
            'Gosto de atividades ao ar livre e esportes.',
            'Amante de livros e filmes.',
            'Sempre em busca de novas aventuras.',
            'Gosto de cozinhar e experimentar novos sabores.',
            'Apaixonada por dança e movimento.',
            'Adoro animais e natureza.',
            'Gosto de tecnologia e inovação.',
            'Apaixonada por fotografia e arte visual.'
        ]
        
        for i in range(num_usuarios):
            nome = random.choice(nomes)
            sobrenome = random.choice(sobrenomes)
            email = f"{nome.lower()}.{sobrenome.lower()}{i}@example.com"
            username = f"{nome.lower()}{sobrenome.lower()}{i}"
            
            # Data de nascimento entre 18 e 50 anos
            idade = random.randint(18, 50)
            data_nascimento = date.today() - timedelta(days=idade * 365 + random.randint(0, 365))
            
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                first_name=nome,
                last_name=sobrenome,
                password='demo123',
                data_nascimento=data_nascimento,
                genero=random.choice(generos),
                genero_interesse=random.choice(generos_interesse),
                cidade=random.choice(cidades),
                estado=random.choice(estados),
                bio=random.choice(bios),
                idade_minima=random.randint(18, 30),
                idade_maxima=random.randint(30, 60),
                distancia_maxima=random.randint(10, 100),
                is_vip=random.choice([True, False]),
                is_verificado=random.choice([True, False])
            )
            
            # Criar algumas assinaturas
            if usuario.is_vip and random.random() < 0.7:
                plano = random.choice(PlanoAssinatura.objects.all())
                Assinatura.objects.create(
                    usuario=usuario,
                    plano=plano,
                    tipo=random.choice(['mensal', 'anual']),
                    data_inicio=timezone.now() - timedelta(days=random.randint(1, 30)),
                    data_fim=timezone.now() + timedelta(days=random.randint(1, 365)),
                    valor_pago=plano.preco_mensal,
                    status='ativa'
                )
        
        self.stdout.write(f'{num_usuarios} usuários criados')

    def criar_postagens(self):
        """Criar postagens de exemplo"""
        usuarios = Usuario.objects.all()
        conteudos = [
            'Acabei de chegar de uma viagem incrível! 🌍',
            'Que dia lindo para um passeio no parque! ☀️',
            'Experimentei um restaurante novo hoje, estava delicioso! 🍽️',
            'Assistindo um filme incrível, recomendo! 🎬',
            'Dia de malhar na academia! 💪',
            'Encontrei um livro fantástico, não consigo parar de ler! 📚',
            'Café da manhã perfeito! ☕',
            'Aprendendo uma nova habilidade, é sempre bom evoluir! 🎯',
            'Dia de relaxar e recarregar as energias! 😌',
            'Conheci pessoas incríveis hoje! 👥'
        ]
        
        tipos = ['texto', 'imagem', 'localizacao']
        
        for usuario in usuarios:
            num_postagens = random.randint(1, 5)
            for _ in range(num_postagens):
                Postagem.objects.create(
                    autor=usuario,
                    conteudo=random.choice(conteudos),
                    tipo=random.choice(tipos),
                    localizacao=random.choice([
                        'Parque Ibirapuera, São Paulo',
                        'Praia de Copacabana, Rio de Janeiro',
                        'Centro de Belo Horizonte',
                        'Pelourinho, Salvador',
                        'Parque da Cidade, Brasília'
                    ]) if random.random() < 0.3 else '',
                    data_criacao=timezone.now() - timedelta(days=random.randint(0, 30))
                )
        
        self.stdout.write('Postagens criadas')

    def criar_relacionamentos(self):
        """Criar relacionamentos entre usuários"""
        usuarios = list(Usuario.objects.all())
        tipos = ['like', 'dislike', 'match', 'super_like']
        
        for _ in range(len(usuarios) * 3):
            remetente = random.choice(usuarios)
            destinatario = random.choice([u for u in usuarios if u != remetente])
            tipo = random.choice(tipos)
            
            # Verificar se já existe relacionamento
            if not Relacionamento.objects.filter(remetente=remetente, destinatario=destinatario).exists():
                Relacionamento.objects.create(
                    remetente=remetente,
                    destinatario=destinatario,
                    tipo=tipo,
                    data_criacao=timezone.now() - timedelta(days=random.randint(0, 15))
                )
        
        self.stdout.write('Relacionamentos criados')

    def criar_conversas(self):
        """Criar conversas entre usuários"""
        usuarios = list(Usuario.objects.all())
        
        # Criar algumas conversas
        for _ in range(min(10, len(usuarios) // 2)):
            participantes = random.sample(usuarios, 2)
            conversa = Conversa.objects.create()
            conversa.participantes.set(participantes)
            
            # Criar algumas mensagens
            num_mensagens = random.randint(3, 10)
            mensagens = [
                'Oi! Como você está?',
                'Tudo bem, obrigado! E você?',
                'Estou bem também! Vi seu perfil e achei interessante.',
                'Obrigado! O seu também é muito legal.',
                'Que bom! Você gosta de viajar?',
                'Sim, adoro! E você?',
                'Também! Qual foi sua última viagem?',
                'Fui para a praia no final de semana.',
                'Que legal! Eu gosto muito da praia também.',
                'Que coincidência! Talvez possamos ir juntos algum dia.'
            ]
            
            for i in range(num_mensagens):
                remetente = participantes[i % 2]
                Mensagem.objects.create(
                    conversa=conversa,
                    remetente=remetente,
                    conteudo=random.choice(mensagens),
                    data_criacao=timezone.now() - timedelta(hours=random.randint(0, 48))
                )
        
        self.stdout.write('Conversas criadas')
