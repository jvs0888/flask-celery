import os
import json
from pathlib import Path
from dotenv import load_dotenv


class Config:
    def __init__(self):
        self.config_path: Path = Path(__file__).resolve().parent
        self.project_path: Path = Path(self.config_path).parent
        self.env_path: str = os.path.join(self.config_path, '.env')
        self.read_config()
        load_dotenv(dotenv_path=self.env_path)

    def __getattr__(self, attr: str) -> str:
        return os.getenv(attr)

    def read_config(self) -> None:
        files: list = [file for file in os.listdir(self.config_path) if file.endswith('.json')]
        for file in files:
            file_path: str = os.path.join(self.config_path, file)
            with open(file=file_path, mode='r', encoding='utf-8') as cfg:
                setattr(self, file[:-5], json.loads(cfg.read()))


config: Config = Config()
