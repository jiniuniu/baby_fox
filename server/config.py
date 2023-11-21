from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()


class EnvironmentSettings(BaseSettings):
    OPENAI_API_KEY: str
    KNOWN_ACCESS_TOKENS: list[str]
    AGENT_DB_ROOT: str
    E2B_API_KEY: str
    MARTECH_KB_ENDPOINT: str
    MARTECH_KB_TOKEN: str
    TIAN_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


env_settings = EnvironmentSettings()
