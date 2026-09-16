from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Lê o .env na raiz do projeto. `extra="ignore"` faz o pydantic ignorar
    # variáveis do .env que não estão declaradas aqui (ex.: as MYSQL_* do Docker).
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Identidade da API
    APP_NAME: str = "ASTRA — Sistema de Gestão Escolar"
    APP_VERSION: str = "0.1.0"

    # Conexão com o banco (obrigatória — vem do .env)
    DATABASE_URL: str

    # Se True, o SQLAlchemy imprime todo SQL executado (útil para depurar)
    DB_ECHO: bool = False

    # Segurança / JWT (tutorial 04)
    SECRET_KEY: str                      # obrigatória — vem do .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


# Instância única, importada por todo o projeto.
settings = Settings()
