from django.core.management.base import BaseCommand
from django.utils import timezone
from usuarios.models import Cidade
import requests
from datetime import timedelta


class Command(BaseCommand):
    help = 'Atualiza dados de cidades da API IBGE (apenas cidades existentes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            help='Atualizar apenas cidades não atualizadas nos últimos X dias',
            default=30
        )
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Forçar atualização de todas as cidades'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        forcar = options['forcar']
        
        if forcar:
            cidades_para_atualizar = Cidade.objects.filter(ativa=True)
            self.stdout.write(f'Atualizando {cidades_para_atualizar.count()} cidades...')
        else:
            data_limite = timezone.now() - timedelta(days=dias)
            cidades_para_atualizar = Cidade.objects.filter(
                ativa=True,
                data_atualizacao__lt=data_limite
            )
            self.stdout.write(f'Atualizando {cidades_para_atualizar.count()} cidades não atualizadas nos últimos {dias} dias...')
        
        atualizadas = 0
        erros = 0
        
        for cidade in cidades_para_atualizar:
            try:
                dados_atualizados = self.buscar_dados_cidade(cidade.codigo_ibge)
                
                if dados_atualizados:
                    # Verificar se houve mudanças
                    mudancas = False
                    
                    if cidade.latitude != dados_atualizados['latitude']:
                        cidade.latitude = dados_atualizados['latitude']
                        mudancas = True
                    
                    if cidade.longitude != dados_atualizados['longitude']:
                        cidade.longitude = dados_atualizados['longitude']
                        mudancas = True
                    
                    if cidade.populacao != dados_atualizados.get('populacao'):
                        cidade.populacao = dados_atualizados.get('populacao')
                        mudancas = True
                    
                    if mudancas:
                        cidade.save()
                        atualizadas += 1
                        self.stdout.write(f'  ✓ Atualizada: {cidade.nome_completo}')
                    else:
                        # Apenas atualizar timestamp
                        cidade.save(update_fields=['data_atualizacao'])
                        self.stdout.write(f'  = Sem mudanças: {cidade.nome_completo}')
                
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Erro ao atualizar {cidade.nome_completo}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Atualização concluída! {atualizadas} cidades atualizadas, {erros} erros.'
            )
        )

    def buscar_dados_cidade(self, codigo_ibge):
        """Busca dados atualizados de uma cidade"""
        url = f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo_ibge}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Buscar população atual
            populacao = None
            try:
                url_pop = f'https://servicodados.ibge.gov.br/api/v1/pesquisas/6579/resultados/{codigo_ibge}'
                pop_response = requests.get(url_pop)
                if pop_response.status_code == 200:
                    pop_data = pop_response.json()
                    if pop_data and len(pop_data) > 0:
                        populacao = pop_data[0].get('res', {}).get('2022')
            except:
                pass
            
            return {
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'populacao': populacao
            }
        
        return None
