# 💕 Me Ache - Rede Social de Encontros

Um aplicativo web moderno de encontros e conexões sociais desenvolvido com Django e Bootstrap 5.

## 🚀 Características

### ✨ Funcionalidades Principais
- **Sistema de Usuários**: Cadastro, login e perfis personalizados
- **Feed Social**: Postagens com texto, imagens e vídeos
- **Sistema de Matches**: Like, dislike e super like
- **Chat Interno**: Mensagens em tempo real
- **Sistema VIP**: Planos de assinatura com recursos exclusivos
- **Filtros Avançados**: Busca por localização, idade e preferências
- **Interface Responsiva**: Design moderno para mobile e desktop

### 🛠️ Tecnologias Utilizadas
- **Backend**: Django 4.2.7 (Python)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Arquitetura**: MVC (Model-View-Controller)
- **Padrões**: POO, Componentização, Clean Code

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Git

## 🚀 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd meache_test
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Para PostgreSQL (opcional)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=meache_db
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_HOST=localhost
DB_PORT=5432
```

### 5. Execute as migrações
```bash
python manage.py migrate
```

### 6. Crie dados de exemplo (opcional)
```bash
python manage.py populate_data --users 20
```

### 7. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 8. Execute o servidor
```bash
python manage.py runserver
```

## 🌐 Acesso ao Sistema

- **Aplicação**: http://127.0.0.1:8000
- **Admin**: http://127.0.0.1:8000/admin
- **Usuário Admin**: admin / admin123

## 📱 Funcionalidades Detalhadas

### 👤 Sistema de Usuários
- Cadastro com validação de idade (18+)
- Perfil personalizado com foto, bio e preferências
- Configurações de privacidade
- Sistema de verificação de contas

### 📱 Feed Social
- Postagens com texto, imagem e vídeo
- Sistema de curtidas e comentários
- Compartilhamento de localização
- Paginação e filtros

### 💬 Chat Interno
- Conversas privadas entre usuários
- Mensagens em tempo real (AJAX)
- Indicadores de mensagens lidas
- Interface similar ao WhatsApp

### 💎 Sistema VIP
- **Plano Básico**: R$ 19,90/mês
- **Plano Premium**: R$ 39,90/mês
- **Plano VIP**: R$ 79,90/mês
- Recursos exclusivos: likes ilimitados, filtros avançados, etc.

### 🔍 Filtros e Busca
- Busca por nome, cidade, idade
- Filtros por gênero e preferências
- Localização geográfica
- Usuários online/VIP

## 🗂️ Estrutura do Projeto

```
meache_test/
├── meache/                 # Configurações principais
│   ├── settings.py        # Configurações do Django
│   ├── urls.py           # URLs principais
│   └── wsgi.py           # WSGI configuration
├── usuarios/              # App de usuários
│   ├── models.py         # Modelo de usuário personalizado
│   ├── views.py          # Views de autenticação e perfil
│   ├── forms.py          # Formulários de usuário
│   └── admin.py          # Interface administrativa
├── feed/                 # App do feed social
│   ├── models.py         # Modelos de postagens e interações
│   ├── views.py          # Views do feed
│   └── forms.py          # Formulários de postagem
├── chat/                 # App de chat
│   ├── models.py         # Modelos de conversas e mensagens
│   └── views.py          # Views do chat
├── assinaturas/          # App de assinaturas VIP
│   ├── models.py         # Modelos de planos e pagamentos
│   └── views.py          # Views de assinaturas
├── templates/            # Templates HTML
│   ├── base/            # Templates base
│   ├── usuarios/        # Templates de usuários
│   ├── feed/            # Templates do feed
│   ├── chat/            # Templates do chat
│   └── assinaturas/     # Templates de assinaturas
├── static/              # Arquivos estáticos
│   ├── css/            # Estilos CSS
│   ├── js/             # JavaScript
│   └── images/         # Imagens
└── requirements.txt     # Dependências Python
```

## 🎨 Design e UX

### Características do Design
- **Mobile First**: Design responsivo para todos os dispositivos
- **Bootstrap 5**: Framework CSS moderno
- **Cores**: Paleta rosa/vermelho para tema de relacionamentos
- **Componentes**: Cards, modais, formulários reutilizáveis
- **Animações**: Transições suaves e micro-interações

### Componentes Principais
- **Navbar**: Navegação principal com dropdown de usuário
- **Cards de Perfil**: Exibição de usuários com ações
- **Feed Cards**: Postagens com interações
- **Chat Interface**: Conversas com mensagens
- **Modais**: Filtros e configurações

## 🔧 Comandos Úteis

### Desenvolvimento
```bash
# Executar servidor
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Shell interativo
python manage.py shell

# Coletar arquivos estáticos
python manage.py collectstatic
```

### Dados de Exemplo
```bash
# Popular com dados de exemplo
python manage.py populate_data --users 50

# Limpar banco de dados
python manage.py flush
```

## 🚀 Deploy

### Para Produção
1. Configure PostgreSQL
2. Defina `DEBUG=False`
3. Configure `ALLOWED_HOSTS`
4. Use `python manage.py collectstatic`
5. Configure servidor web (Nginx + Gunicorn)

### Variáveis de Ambiente de Produção
```env
SECRET_KEY=sua_chave_secreta_super_segura
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=meache_prod
DB_USER=usuario_db
DB_PASSWORD=senha_super_segura
DB_HOST=localhost
DB_PORT=5432
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Equipe

- **Desenvolvedor Principal**: [Seu Nome]
- **Design**: Bootstrap 5 + Custom CSS
- **Backend**: Django + Python

## 📞 Suporte

Para suporte, envie um email para suporte@meache.com ou abra uma issue no GitHub.

---

**Me Ache** - Conectando pessoas especiais através de encontros autênticos e relacionamentos significativos. 💕
