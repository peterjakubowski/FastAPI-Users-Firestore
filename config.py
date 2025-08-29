from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and secrets.
    """

    GOOGLE_APPLICATION_CREDENTIALS: str
    AUTHENTICATION_BACKEND_SECRET: str
    RESET_PASSWORD_TOKEN_SECRET: str
    VERIFICATION_TOKEN_SECRET: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


# Create a single instance of the Settings class
settings = Settings()
