# ASTRA — Sistema de Gestão Escolar

Projeto integrador construído ao longo da série de tutoriais **Projeto ASTRA com FastAPI**.
Stack: FastAPI · SQLAlchemy · MySQL 8 (Docker) · JWT · Jinja2 · Bootstrap 5.

## Estado atual — Etapa 04 (Autenticação & RBAC)

A API agora tem login. Nasceram os primeiros modelos mapeados (`usuario`, `perfil`,
`permissao`), o núcleo de segurança (hash de senha com bcrypt + JWT com PyJWT) e a
máquina de autorização: `get_current_user` e `requer_permissao(...)`.

## Como rodar e autenticar

```bash
# 1. Segredos (gere a SECRET_KEY!)
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # cole em SECRET_KEY

# 2. Banco em container
docker compose up -d

# 3. Ambiente Python
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 4. Criar o primeiro administrador
python criar_admin.py           # admin@astra.local / admin123

# 5. Subir a API
uvicorn app.main:app --reload
```

Depois, em `http://localhost:8000/docs`:
1. `POST /auth/login` com `username = admin@astra.local` e `password = admin123`.
2. Clique em **Authorize** e cole o token (ou use o próprio fluxo do Swagger).
3. Teste `GET /auth/me` e `GET /auth/minhas-permissoes`.

## Estrutura (etapa 04)

```
astra/
├── docker-compose.yml
├── script.sql
├── .env / .env.example
├── requirements.txt
├── criar_admin.py           # cria o admin inicial
├── README.md
└── app/
    ├── __init__.py
    ├── config.py            # + SECRET_KEY, ALGORITHM, expiração
    ├── database.py
    ├── main.py              # + registra o router de auth
    ├── core/
    │   ├── __init__.py
    │   ├── security.py      # hash de senha + JWT
    │   └── deps.py          # get_current_user + requer_permissao
    ├── models/
    │   ├── __init__.py
    │   ├── associations.py  # usuario_perfil, perfil_permissao
    │   ├── usuario.py
    │   ├── perfil.py
    │   └── permissao.py
    ├── schemas/
    │   ├── __init__.py
    │   └── auth.py
    └── routers/
        ├── __init__.py
        └── auth.py
```

As próximas etapas adicionam: CRUDs (curso, disciplina), domínio acadêmico e front-end.
