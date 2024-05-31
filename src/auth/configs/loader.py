import json
import os
from urllib.request import urlretrieve

from dotenv import load_dotenv
from pydantic import Field

from src.core.configs.base import ProjectSettings

load_dotenv(".env")


class LoaderSettings(ProjectSettings):
    google_url: str = Field(..., alias="AUTH_GOOGLE_CONFIG_URL")

    def download_file(self, url: str) -> str:
        file_name = url.split("/")[2]
        file_path = f"{os.path.dirname(self.base_dir)}/auth/configs/{file_name}"
        urlretrieve(url, file_path)

        return file_path

    def get_JSON_config(self, url: str) -> dict[str, str]:
        file_path = self.download_file(url)
        with open(file_path) as json_file:
            data = json.load(json_file)
            return data
