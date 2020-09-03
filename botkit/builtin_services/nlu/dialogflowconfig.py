from pathlib import Path

from dataclasses import dataclass


@dataclass
class DialogflowConfig:
    project_id: str
    json_credentials_file: Path or str

    KEY = 'dialogflow_config'