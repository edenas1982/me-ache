from django import forms
from .models import Postagem, Comentario


class PostagemForm(forms.ModelForm):
    """Formulário para criar/editar postagens"""
    
    class Meta:
        model = Postagem
        fields = ['conteudo', 'tipo', 'imagem', 'video', 'localizacao']
        widgets = {
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'O que você está pensando?',
                'rows': 4
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
            'localizacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Onde você está?'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conteudo'].required = True
        self.fields['tipo'].initial = 'texto'
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        imagem = cleaned_data.get('imagem')
        video = cleaned_data.get('video')
        
        if tipo == 'imagem' and not imagem:
            raise forms.ValidationError('Selecione uma imagem para postagens do tipo imagem.')
        
        if tipo == 'video' and not video:
            raise forms.ValidationError('Selecione um vídeo para postagens do tipo vídeo.')
        
        return cleaned_data


class ComentarioForm(forms.ModelForm):
    """Formulário para comentários"""
    
    class Meta:
        model = Comentario
        fields = ['conteudo']
        widgets = {
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escreva um comentário...',
                'rows': 2
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conteudo'].required = True
