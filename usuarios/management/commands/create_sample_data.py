from django.core.management.base import BaseCommand
from usuarios.models import Interesse, Objetivo, Fetiche


class Command(BaseCommand):
    help = 'Cria dados de exemplo para interesses, objetivos e fetiches'

    def handle(self, *args, **options):
        # Criar Interesses
        interesses_data = [
            ('Amizade', 'Para fazer amigos e socializar'),
            ('Relacionamento sério', 'Para um relacionamento duradouro'),
            ('Encontro casual', 'Para encontros casuais'),
            ('Ficar', 'Para ficar sem compromisso'),
            ('Networking', 'Para contatos profissionais'),
            ('Viagem', 'Para companhia de viagem'),
            ('Atividade física', 'Para praticar esportes juntos'),
            ('Cultura', 'Para eventos culturais'),
            ('Música', 'Para shows e festivais'),
            ('Gastronomia', 'Para experimentar restaurantes'),
        ]

        for nome, descricao in interesses_data:
            Interesse.objects.get_or_create(
                nome=nome,
                defaults={'descricao': descricao}
            )

        # Criar Objetivos
        objetivos_data = [
            ('Namoro', 'Busco um relacionamento sério'),
            ('Casamento', 'Busco alguém para casar'),
            ('Amizade colorida', 'Amizade com benefícios'),
            ('Companhia', 'Apenas companhia e conversa'),
            ('Aventura', 'Busco experiências novas'),
            ('Estabilidade', 'Busco estabilidade emocional'),
            ('Diversão', 'Apenas diversão e lazer'),
            ('Crescimento pessoal', 'Busco crescer como pessoa'),
            ('Família', 'Busco formar uma família'),
            ('Liberdade', 'Busco relacionamento livre'),
        ]

        for nome, descricao in objetivos_data:
            Objetivo.objects.get_or_create(
                nome=nome,
                defaults={'descricao': descricao}
            )

        # Criar Fetiches
        fetiches_data = [
            ('Romance', 'Gosto de romance e carinho'),
            ('Aventura', 'Gosto de aventuras e adrenalina'),
            ('Cozinha', 'Gosto de cozinhar juntos'),
            ('Viagem', 'Amo viajar'),
            ('Esportes', 'Gosto de praticar esportes'),
            ('Música', 'Amo música e dança'),
            ('Arte', 'Gosto de arte e cultura'),
            ('Natureza', 'Amo estar na natureza'),
            ('Tecnologia', 'Gosto de tecnologia'),
            ('Leitura', 'Amo ler'),
            ('Filmes', 'Gosto de assistir filmes'),
            ('Jogos', 'Gosto de jogar'),
            ('Fotografia', 'Amo fotografar'),
            ('Moda', 'Gosto de moda e estilo'),
            ('Beleza', 'Gosto de cuidar da beleza'),
        ]

        for nome, descricao in fetiches_data:
            Fetiche.objects.get_or_create(
                nome=nome,
                defaults={'descricao': descricao}
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Criados {len(interesses_data)} interesses, '
                f'{len(objetivos_data)} objetivos e '
                f'{len(fetiches_data)} fetiches com sucesso!'
            )
        )

