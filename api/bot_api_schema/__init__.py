import json
from pathlib import Path
from typing import List, Dict


with open(Path(__file__).parent / "bot_api_schema.json", "r", encoding="utf-8") as fp:
    bot_api_schema: List[Dict] = json.load(fp)


# def get_methods():
#     return [x for x in ]
