from django.core.management.base import BaseCommand
from usuarios.models import EstadoCivil, Etnia, TipoCorpo, NivelAbertura, Signo, CorOlhos, CorCabelos


class Command(BaseCommand):
    help = 'Popula dados iniciais para os modelos de perfil'

    def handle(self, *args, **options):
        self.stdout.write('Populando dados iniciais...')
        
        # Estados Civis
        estados_civis = [
            ('Solteiro(a)', 1),
            ('Namorando', 2),
            ('Casado(a)', 3),
            ('União Estável', 4),
            ('Divorciado(a)', 5),
            ('Viúvo(a)', 6),
        ]
        
        for nome, ordem in estados_civis:
            EstadoCivil.objects.get_or_create(
                nome=nome,
                defaults={'ordem': ordem, 'ativo': True}
            )
        
        # Etnias
        etnias = [
            ('Branco', 1),
            ('Negro', 2),
            ('Pardo', 3),
            ('Amarelo', 4),
            ('Indígena', 5),
            ('Outro', 6),
        ]
        
        for nome, ordem in etnias:
            Etnia.objects.get_or_create(
                nome=nome,
                defaults={'ordem': ordem, 'ativo': True}
            )
        
        # Tipos de Corpo
        tipos_corpo = [
            ('Magro', 1),
            ('Atlético', 2),
            ('Normal', 3),
            ('Acima do peso', 4),
            ('Musculoso', 5),
        ]
        
        for nome, ordem in tipos_corpo:
            TipoCorpo.objects.get_or_create(
                nome=nome,
                defaults={'ordem': ordem, 'ativo': True}
            )
        
        # Níveis de Abertura
        niveis_abertura = [
            ('Conservador', 'Prefere relacionamentos mais tradicionais', 1),
            ('Moderado', 'Aberto a algumas experiências', 2),
            ('Aberto', 'Aberto a diversas experiências', 3),
            ('Muito Aberto', 'Muito aberto a experiências variadas', 4),
        ]
        
        for nome, descricao, ordem in niveis_abertura:
            NivelAbertura.objects.get_or_create(
                nome=nome,
                defaults={'descricao': descricao, 'ordem': ordem, 'ativo': True}
            )
        
        # Signos
        signos = [
            ('Áries', '21/03', '20/04', 1),
            ('Touro', '21/04', '20/05', 2),
            ('Gêmeos', '21/05', '20/06', 3),
            ('Câncer', '21/06', '21/07', 4),
            ('Leão', '22/07', '22/08', 5),
            ('Virgem', '23/08', '22/09', 6),
            ('Libra', '23/09', '22/10', 7),
            ('Escorpião', '23/10', '21/11', 8),
            ('Sagitário', '22/11', '21/12', 9),
            ('Capricórnio', '22/12', '20/01', 10),
            ('Aquário', '21/01', '19/02', 11),
            ('Peixes', '20/02', '20/03', 12),
        ]
        
        for nome, inicio, fim, ordem in signos:
            Signo.objects.get_or_create(
                nome=nome,
                defaults={
                    'data_inicio': inicio,
                    'data_fim': fim,
                    'ordem': ordem,
                    'ativo': True
                }
            )
        
        # Cores dos Olhos
        cores_olhos = [
            ('Pretos', 1),
            ('Castanhos', 2),
            ('Azuis', 3),
            ('Verdes', 4),
            ('Cinzas', 5),
            ('Mel', 6),
            ('Outro', 7),
        ]
        
        for nome, ordem in cores_olhos:
            CorOlhos.objects.get_or_create(
                nome=nome,
                defaults={'ordem': ordem, 'ativo': True}
            )
        
        # Cores dos Cabelos
        cores_cabelos = [
            ('Pretos', 1),
            ('Castanhos', 2),
            ('Loiros', 3),
            ('Ruivos', 4),
            ('Grisalhos', 5),
            ('Outro', 6),
        ]
        
        for nome, ordem in cores_cabelos:
            CorCabelos.objects.get_or_create(
                nome=nome,
                defaults={'ordem': ordem, 'ativo': True}
            )
        
        self.stdout.write(
            self.style.SUCCESS('Dados iniciais populados com sucesso!')
        )
