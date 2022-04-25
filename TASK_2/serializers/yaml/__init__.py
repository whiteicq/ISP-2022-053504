import yaml
import sys
from typing import IO
from parser import ISerializer

sys.path.insert(0, "/home/vlad/Рабочий стол/ISP/TASK_2")

class YAML(ISerializer):

    def dump(self, obj: dict, fp: IO) -> None:
        yaml.dump(obj, fp)

    def dumps(self, obj: dict) -> str:
        return yaml.dump(obj)

    def load(self, fp: IO) -> dict:
        return yaml.load(fp)

    def loads(self, s: str) -> dict:
        return yaml.load(s)
