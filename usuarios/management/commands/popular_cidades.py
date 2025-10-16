from django.core.management.base import BaseCommand
from django.db import transaction
import requests
import time
from usuarios.models import Cidade


class Command(BaseCommand):
    help = 'Popula a tabela de cidades com dados da API do IBGE'

    def add_arguments(self, parser):
        parser.add_argument(
            '--estados',
            type=str,
            help='Estados para popular (ex: PR,SP,RJ) ou "all" para todos',
            default='PR'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpar tabela antes de popular'
        )

    def handle(self, *args, **options):
        estados = options['estados']
        limpar = options['limpar']
        
        if limpar:
            self.stdout.write('Limpando tabela de cidades...')
            Cidade.objects.all().delete()
        
        if estados == 'all':
            # Buscar todos os estados
            estados_lista = self.buscar_estados()
        else:
            estados_lista = [estado.strip().upper() for estado in estados.split(',')]
        
        total_cidades = 0
        
        for estado in estados_lista:
            self.stdout.write(f'Processando estado: {estado}')
            cidades_estado = self.buscar_cidades_estado(estado)
            
            with transaction.atomic():
                for cidade_data in cidades_estado:
                    cidade, created = Cidade.objects.get_or_create(
                        codigo_ibge=cidade_data['codigo_ibge'],
                        defaults={
                            'nome': cidade_data['nome'],
                            'estado': cidade_data['estado'],
                            'latitude': cidade_data['latitude'],
                            'longitude': cidade_data['longitude'],
                            'populacao': cidade_data.get('populacao'),
                            'ativa': True
                        }
                    )
                    
                    if created:
                        total_cidades += 1
                        self.stdout.write(f'  ✓ Criada: {cidade.nome_completo}')
                    else:
                        # Atualizar dados se necessário
                        updated = False
                        if cidade.latitude != cidade_data['latitude']:
                            cidade.latitude = cidade_data['latitude']
                            updated = True
                        if cidade.longitude != cidade_data['longitude']:
                            cidade.longitude = cidade_data['longitude']
                            updated = True
                        if cidade.populacao != cidade_data.get('populacao'):
                            cidade.populacao = cidade_data.get('populacao')
                            updated = True
                        
                        if updated:
                            cidade.save()
                            self.stdout.write(f'  ↻ Atualizada: {cidade.nome_completo}')
            
            # Pausa para não sobrecarregar a API
            time.sleep(0.5)
        
        self.stdout.write(
            self.style.SUCCESS(f'Processamento concluído! {total_cidades} cidades processadas.')
        )

    def buscar_estados(self):
        """Busca todos os estados do Brasil"""
        url = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
        response = requests.get(url)
        
        if response.status_code == 200:
            estados = response.json()
            return [estado['sigla'] for estado in estados]
        else:
            self.stdout.write(
                self.style.ERROR('Erro ao buscar estados da API IBGE')
            )
            return []

    def buscar_cidades_estado(self, estado):
        """Busca cidades de um estado específico"""
        url = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado}/municipios'
        response = requests.get(url)
        
        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR(f'Erro ao buscar cidades do estado {estado}')
            )
            return []
        
        cidades = response.json()
        cidades_processadas = []
        
        for cidade in cidades:
            # Buscar coordenadas da cidade
            coordenadas = self.buscar_coordenadas_cidade(cidade['id'])
            
            if coordenadas:
                cidades_processadas.append({
                    'codigo_ibge': str(cidade['id']),
                    'nome': cidade['nome'],
                    'estado': estado,
                    'latitude': coordenadas['latitude'],
                    'longitude': coordenadas['longitude'],
                    'populacao': coordenadas.get('populacao')
                })
        
        return cidades_processadas

    def buscar_coordenadas_cidade(self, codigo_ibge):
        """Busca coordenadas e população de uma cidade específica"""
        # API do IBGE para coordenadas
        url = f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo_ibge}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # A API do IBGE não retorna coordenadas diretamente
            # Vamos usar uma abordagem diferente - buscar por nome da cidade
            nome_cidade = data.get('nome', '')
            estado = data.get('microrregiao', {}).get('mesorregiao', {}).get('UF', {}).get('sigla', '')
            
            if nome_cidade and estado:
                # Usar API alternativa para coordenadas (Nominatim - OpenStreetMap)
                coordenadas = self.buscar_coordenadas_nominatim(nome_cidade, estado)
                
                if coordenadas:
                    return {
                        'latitude': coordenadas['latitude'],
                        'longitude': coordenadas['longitude'],
                        'populacao': None  # IBGE não fornece população facilmente
                    }
        
        return None
    
    def buscar_coordenadas_nominatim(self, nome_cidade, estado):
        """Busca coordenadas usando Nominatim (OpenStreetMap)"""
        try:
            query = f"{nome_cidade}, {estado}, Brasil"
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'br'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return {
                        'latitude': float(data[0]['lat']),
                        'longitude': float(data[0]['lon'])
                    }
        except Exception as e:
            print(f"Erro ao buscar coordenadas para {nome_cidade}: {e}")
        
        return None
