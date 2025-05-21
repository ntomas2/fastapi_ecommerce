from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    secret_key: str
    algorithm: str
    email_from: str
    smtp_host: str
    smtp_port: str
    smtp_user: str
    smtp_password: str
    rabbitmq_url: str
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
# DB
POSTGRES_DB = settings.postgres_db
POSTGRES_USER = settings.postgres_user
POSTGRES_PASSWORD = settings.postgres_password
# JWT
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
# Email
EMAIL_FROM = settings.email_from
SMTP_HOST = settings.smtp_host
SMTP_PORT = settings.smtp_port
SMTP_USER = settings.smtp_user
SMTP_PASSWORD = settings.smtp_password
# RabbitMQ
RABBITMQ_URL = settings.rabbitmq_url
