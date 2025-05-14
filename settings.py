from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    secret_key: str
    algorithm: str
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
POSTGRES_DB = settings.postgres_db
POSTGRES_USER = settings.postgres_user
POSTGRES_PASSWORD = settings.postgres_password
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm