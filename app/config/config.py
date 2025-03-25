from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str = "localhost"
    database_port: int = 5432
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()