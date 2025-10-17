from django.core.management.base import BaseCommand
from usuarios.models import Usuario, PerfilDetalhado, PerfilInteresses, PerfilSobre


class Command(BaseCommand):
    help = 'Verifica dados salvos no perfil de um usuário'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username do usuário')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            usuario = Usuario.objects.get(username=username)
            self.stdout.write(f'\n=== PERFIL DE {usuario.username.upper()} ===')
            
            # Dados básicos
            self.stdout.write(f'\n📋 DADOS BÁSICOS:')
            self.stdout.write(f'Nome: {usuario.username}')
            self.stdout.write(f'Tipo de Perfil: {usuario.tipo_perfil}')
            self.stdout.write(f'Cidade: {usuario.cidade_ref}')
            self.stdout.write(f'Tipo Relacionamento: {usuario.tipo_relacionamento}')
            self.stdout.write(f'Tempo Juntos: {usuario.tempo_juntos}')
            
            # Perfis detalhados
            perfis_detalhados = PerfilDetalhado.objects.filter(usuario=usuario)
            self.stdout.write(f'\n👤 PERFIS DETALHADOS ({perfis_detalhados.count()}):')
            for perfil in perfis_detalhados:
                self.stdout.write(f'\n  {perfil.get_pessoa_display()}:')
                self.stdout.write(f'    Nome: {perfil.nome_apelido}')
                self.stdout.write(f'    Data Nascimento: {perfil.data_nascimento}')
                self.stdout.write(f'    Profissão: {perfil.profissao}')
                self.stdout.write(f'    Altura: {perfil.altura}cm')
                self.stdout.write(f'    Peso: {perfil.peso}kg')
                self.stdout.write(f'    Signo: {perfil.signo}')
                self.stdout.write(f'    Estado Civil: {perfil.estado_civil}')
                self.stdout.write(f'    Etnia: {perfil.etnia}')
                self.stdout.write(f'    Tipo Corpo: {perfil.tipo_corpo}')
                self.stdout.write(f'    Cor Olhos: {perfil.cor_olhos}')
                self.stdout.write(f'    Cor Cabelos: {perfil.cor_cabelos}')
                self.stdout.write(f'    Orientação: {perfil.orientacao_sexual}')
                self.stdout.write(f'    Fumante: {perfil.fumante}')
                self.stdout.write(f'    Bebe: {perfil.bebe}')
                self.stdout.write(f'    Descrição: {perfil.descricao_pessoal[:50]}...')
            
            # Interesses
            try:
                interesses = PerfilInteresses.objects.get(usuario=usuario)
                self.stdout.write(f'\n💫 INTERESSES:')
                self.stdout.write(f'Nível Abertura: {interesses.nivel_abertura}')
                
                campos_true = []
                for field in interesses._meta.fields:
                    if field.name not in ['id', 'usuario', 'nivel_abertura', 'criado_em', 'atualizado_em']:
                        if getattr(interesses, field.name):
                            campos_true.append(field.verbose_name)
                
                if campos_true:
                    self.stdout.write('Marcados: ' + ', '.join(campos_true))
                else:
                    self.stdout.write('Nenhum interesse marcado')
                    
            except PerfilInteresses.DoesNotExist:
                self.stdout.write('\n💫 INTERESSES: Não encontrado')
            
            # Sobre
            try:
                sobre = PerfilSobre.objects.get(usuario=usuario)
                self.stdout.write(f'\n📖 SOBRE:')
                self.stdout.write(f'Quem Somos: {sobre.quem_somos[:50]}...')
                self.stdout.write(f'Inspiração: {sobre.inspiracao[:50]}...')
                self.stdout.write(f'Frase Destaque: {sobre.frase_destaque}')
                self.stdout.write(f'Instagram: {sobre.instagram}')
                self.stdout.write(f'Outro Link: {sobre.outro_link}')
                self.stdout.write(f'Bio Ele: {sobre.bio_ele[:50]}...')
                self.stdout.write(f'Bio Ela: {sobre.bio_ela[:50]}...')
                self.stdout.write(f'Bio Individual: {sobre.bio_individual[:50]}...')
                
            except PerfilSobre.DoesNotExist:
                self.stdout.write('\n📖 SOBRE: Não encontrado')
            
            self.stdout.write(f'\n✅ Verificação concluída!')
            
        except Usuario.DoesNotExist:
            self.stdout.write(f'❌ Usuário "{username}" não encontrado!')
