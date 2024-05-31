from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic.fields import Field
from pydantic_settings import BaseSettings

load_dotenv(".env")


class GoogleSettings(BaseSettings):
    """
    This class is used to store the Google client base settings.
    """

    client_id: str = Field(..., alias="AUTH_GOOGLE_CLIENT_ID")
    client_secret: str = Field(..., alias="AUTH_GOOGLE_CLIENT_SECRET")
    scope: str = "openid email profile"
    redirect_uri: str = Field(..., alias="AUTH_REDIRECT_URI")
    prompt: str = Field(..., alias="AUTH_GOOGLE_PROMPT")

    google_config_url: str = Field(..., alias="AUTH_GOOGLE_CONFIG_URL")
    google_state: SecretStr = Field(..., alias="AUTH_GOOGLE_STATE")

    @property
    def settings_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
            "redirect_uri": self.redirect_uri,
            "prompt": self.prompt,
        }
