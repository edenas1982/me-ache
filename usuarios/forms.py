from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date

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
