from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date

from .models import (
    Usuario, Interesse, Objetivo, Fetiche, TipoRelacionamento,
    DadosPessoaisDetalhados, EstiloVida, IdentidadePreferencias, 
    ConfiguracoesPrivacidade, Signo, CorOlhos, CorCabelos, Cidade
)

Usuario = get_user_model()


class UsuarioRegistrationForm(UserCreationForm):
    """Formulário de cadastro de usuários"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )
    
    data_nascimento = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    genero = forms.ChoiceField(
        choices=Usuario.GENERO_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    genero_interesse = forms.ChoiceField(
        choices=Usuario.GENERO_INTERESSE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    cidade = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sua cidade'
        })
    )
    
    estado = forms.CharField(
        max_length=2,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'UF',
            'maxlength': '2'
        })
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Conte um pouco sobre você...',
            'rows': 4
        })
    )
    
    class Meta:
        model = Usuario
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'data_nascimento', 'genero', 'genero_interesse',
            'cidade', 'estado', 'bio', 'password1', 'password2'
        )
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS aos campos de senha
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Sua senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        })
    
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento:
            hoje = date.today()
            idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
            
            if idade < 18:
                raise ValidationError('Você deve ter pelo menos 18 anos para se cadastrar.')
            
            if idade > 100:
                raise ValidationError('Idade inválida.')
        
        return data_nascimento
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Este email já está sendo usado.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError('Este nome de usuário já está sendo usado.')
        return username


class UsuarioUpdateForm(forms.ModelForm):
    """Formulário para atualizar dados básicos do usuário"""
    
    class Meta:
        model = Usuario
        fields = (
            'first_name', 'last_name', 'email', 'cidade', 'estado',
            'genero_interesse', 'idade_minima', 'idade_maxima',
            'distancia_maxima', 'mostrar_idade', 'mostrar_localizacao'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'genero_interesse': forms.Select(attrs={'class': 'form-control'}),
            'idade_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'max': 100}),
            'idade_maxima': forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'max': 100}),
            'distancia_maxima': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 500}),
            'mostrar_idade': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_localizacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PerfilUpdateForm(forms.ModelForm):
    """Formulário para atualizar perfil do usuário"""
    
    class Meta:
        model = Usuario
        fields = (
            'first_name', 'last_name', 'data_nascimento', 'genero',
            'cidade', 'estado', 'bio', 'foto_perfil'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento:
            hoje = date.today()
            idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
            
            if idade < 18:
                raise ValidationError('Você deve ter pelo menos 18 anos.')
            
            if idade > 100:
                raise ValidationError('Idade inválida.')
        
        return data_nascimento


# ==============================================
# FORMS PARA EDIÇÃO DE PERFIL COM ABAS
# ==============================================

class PerfilGeralForm(forms.ModelForm):
    """Formulário para aba Geral"""
    
    class Meta:
        model = Usuario
        fields = (
            'foto_perfil', 'username', 'tipo_perfil', 
            'tipo_relacionamento', 'tempo_juntos',
            'cidade', 'estado', 'cidade_ref'
        )
        widgets = {
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*',
                'id': 'foto-perfil-input'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do perfil'
            }),
            'tipo_perfil': forms.Select(attrs={
                'class': 'form-control',
                'id': 'tipo-perfil-select'
            }),
            'tipo_relacionamento': forms.Select(attrs={
                'class': 'form-control',
                'id': 'tipo-relacionamento-select'
            }),
            'tempo_juntos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 2 anos, 6 meses, 1 ano e meio'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sua cidade'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF',
                'maxlength': '2'
            }),
            'cidade_ref': forms.HiddenInput(),
        }


class PerfilInformacoesForm(forms.ModelForm):
    """Formulário para aba Informações Pessoais"""
    
    class Meta:
        model = Usuario
        fields = (
            'data_nascimento', 'genero', 'profissao', 'estado_civil', 'orientacao_sexual',
            'first_name_parceiro', 'last_name_parceiro', 'data_nascimento_parceiro',
            'genero_parceiro', 'profissao_parceiro', 'estado_civil_parceiro', 'orientacao_sexual_parceiro',
            'foto_perfil_parceiro'
        )
        widgets = {
            # Campos da primeira pessoa
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'data-nascimento'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-control',
                'id': 'genero'
            }),
            'profissao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sua profissão'
            }),
            'estado_civil': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado civil'
            }),
            'orientacao_sexual': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Orientação sexual'
            }),
            
            # Campos do parceiro
            'first_name_parceiro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do parceiro',
                'id': 'nome-parceiro'
            }),
            'last_name_parceiro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome do parceiro',
                'id': 'sobrenome-parceiro'
            }),
            'data_nascimento_parceiro': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'data-nascimento-parceiro'
            }),
            'genero_parceiro': forms.Select(attrs={
                'class': 'form-control',
                'id': 'genero-parceiro'
            }),
            'profissao_parceiro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Profissão do parceiro'
            }),
            'estado_civil_parceiro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado civil do parceiro'
            }),
            'orientacao_sexual_parceiro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Orientação sexual do parceiro'
            }),
            'foto_perfil_parceiro': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'foto-parceiro-input'
            }),
        }
    
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento:
            hoje = date.today()
            idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
            
            if idade < 18:
                raise ValidationError('Você deve ter pelo menos 18 anos.')
            
            if idade > 100:
                raise ValidationError('Idade inválida.')
        
        return data_nascimento
    
    def clean_data_nascimento_parceiro(self):
        data_nascimento = self.cleaned_data.get('data_nascimento_parceiro')
        if data_nascimento:
            hoje = date.today()
            idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
            
            if idade < 18:
                raise ValidationError('O parceiro deve ter pelo menos 18 anos.')
            
            if idade > 100:
                raise ValidationError('Idade inválida.')
        
        return data_nascimento


class DadosPessoaisForm(forms.ModelForm):
    """Formulário para dados pessoais detalhados"""
    
    class Meta:
        model = DadosPessoaisDetalhados
        fields = (
            'nome_apelido', 'data_nascimento', 'signo', 'altura', 'peso',
            'cor_olhos', 'cor_cabelos', 'profissao_ocupacao', 'cidade_atual', 'origem'
        )
        widgets = {
            'nome_apelido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome ou apelido público'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'signo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'altura': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 175',
                'min': '100',
                'max': '250'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 70',
                'min': '30',
                'max': '300'
            }),
            'cor_olhos': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cor_cabelos': forms.Select(attrs={
                'class': 'form-control'
            }),
            'profissao_ocupacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sua profissão ou ocupação'
            }),
            'cidade_atual': forms.Select(attrs={
                'class': 'form-control'
            }),
            'origem': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Popular opções dos campos
        self.fields['signo'].queryset = Signo.objects.filter(ativo=True).order_by('ordem')
        self.fields['cor_olhos'].queryset = CorOlhos.objects.filter(ativo=True).order_by('ordem')
        self.fields['cor_cabelos'].queryset = CorCabelos.objects.filter(ativo=True).order_by('ordem')
        self.fields['cidade_atual'].queryset = Cidade.objects.filter(ativa=True).order_by('nome')
        self.fields['origem'].queryset = Cidade.objects.filter(ativa=True).order_by('nome')


class EstiloVidaForm(forms.ModelForm):
    """Formulário para estilo de vida"""
    
    class Meta:
        model = EstiloVida
        fields = (
            'fumante', 'bebe', 'pratica_esportes', 'tem_filhos', 'tatuagens_piercings'
        )
        widgets = {
            'fumante': forms.Select(attrs={
                'class': 'form-control'
            }),
            'bebe': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pratica_esportes': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tem_filhos': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tatuagens_piercings': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class IdentidadePreferenciasForm(forms.ModelForm):
    """Formulário para identidade e preferências"""
    
    class Meta:
        model = IdentidadePreferencias
        fields = (
            'genero', 'orientacao_sexual', 'aberto_contatos_com'
        )
        widgets = {
            'genero': forms.Select(attrs={
                'class': 'form-control'
            }),
            'orientacao_sexual': forms.Select(attrs={
                'class': 'form-control'
            }),
            'aberto_contatos_com': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class ConfiguracoesPrivacidadeForm(forms.ModelForm):
    """Formulário para configurações de privacidade"""
    
    class Meta:
        model = ConfiguracoesPrivacidade
        fields = (
            'mostrar_idade', 'mostrar_cidade', 'disponivel_mensagens'
        )
        widgets = {
            'mostrar_idade': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_cidade': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'disponivel_mensagens': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class PerfilInteressesForm(forms.Form):
    """Formulário para aba Interesses"""
    
    interesses = forms.ModelMultipleChoiceField(
        queryset=Interesse.objects.filter(ativo=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label="Procurando por"
    )
    
    objetivos = forms.ModelMultipleChoiceField(
        queryset=Objetivo.objects.filter(ativo=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label="Objetivos"
    )
    
    fetiches = forms.ModelMultipleChoiceField(
        queryset=Fetiche.objects.filter(ativo=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label="Fetiches e Preferências"
    )


class PerfilBioForm(forms.ModelForm):
    """Formulário para aba Sobre (Bio)"""
    
    class Meta:
        model = Usuario
        fields = ('bio',)
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'maxlength': 1000,
                'placeholder': 'Conte um pouco sobre você (ou sobre o casal)...',
                'id': 'bio-textarea'
            })
        }
    
    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if bio:
            # Filtro básico de termos proibidos (pode ser expandido)
            termos_proibidos = ['spam', 'promoção', 'venda']
            bio_lower = bio.lower()
            
            for termo in termos_proibidos:
                if termo in bio_lower:
                    raise ValidationError(f'O texto contém termos não permitidos.')
        
        return bio


class BuscaUsuariosForm(forms.Form):
    """Formulário para busca de usuários"""
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome ou username...'
        })
    )
    
    cidade = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cidade...'
        })
    )
    
    idade_min = forms.IntegerField(
        required=False,
        min_value=18,
        max_value=100,
        initial=18,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 18,
            'max': 100
        })
    )
    
    idade_max = forms.IntegerField(
        required=False,
        min_value=18,
        max_value=100,
        initial=50,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 18,
            'max': 100
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        idade_min = cleaned_data.get('idade_min')
        idade_max = cleaned_data.get('idade_max')
        
        if idade_min and idade_max and idade_min > idade_max:
            raise ValidationError('A idade mínima deve ser menor que a máxima.')
        
        return cleaned_data
