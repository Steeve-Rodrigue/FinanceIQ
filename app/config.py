from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FinanceIQ"
    environment: str = "development"
    debug: bool = False
    database_url: str
    # DDL owner role, used only by Alembic — the app itself connects via `database_url` as a
    # restricted, non-superuser role so Postgres row-level security actually applies to it.
    migration_database_url: str | None = None
    log_level: str = "INFO"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
