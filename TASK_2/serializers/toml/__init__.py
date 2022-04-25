import toml
import sys
from typing import IO, Any, Union
from parser import ISerializer
from .constants import STRING_TO_OBJECT_DICT, OBJECT_TO_STRING_DICT


class TOML(ISerializer):

    def _restore_object_dict(self, obj: Any) -> Any:
        object_type = type(obj)
        if object_type is dict:
            if len(obj.keys()) == 1:
                k, v = list(obj.items())[0]
                if k == "None":
                    return None
                elif k in STRING_TO_OBJECT_DICT:
                    return STRING_TO_OBJECT_DICT[k](v)
            result = {}
            for k, v in obj.items():
                result[k] = self._restore_object_dict(v)
            return result
        else:
            return [self._restore_object_dict(item) for item in obj]

    def _adapt_object_dict(self, obj: Any) -> Any:
        object_type = type(obj)
        if object_type is dict:
            result = {}
            for k, v in obj.items():
                result[k] = self._adapt_object_dict(v)
            return result
        elif object_type is list:
            return [self._adapt_object_dict(item) for item in obj]
        elif object_type in OBJECT_TO_STRING_DICT:
            return {
                OBJECT_TO_STRING_DICT[object_type]: str(obj)
            }
        elif object_type is type(None):
            return {
                "None": "None"
            }

    def dump(self, obj: dict, fp: IO) -> None:
        toml.dump(self._adapt_object_dict(obj), fp)

    def dumps(self, obj: dict) -> str:
        return toml.dumps(self._adapt_object_dict(obj))

    def load(self, fp: IO) -> dict:
        return self._restore_object_dict(toml.load(fp))

    def loads(self, s: str) -> dict:
        return self._restore_object_dict(toml.loads(s))
