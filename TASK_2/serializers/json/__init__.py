import re
import sys
from typing import IO, Any, Union
from parser import ISerializer

sys.path.append("/home/vlad/Рабочий стол/ISP/TASK_2")
NONE_STRING = "null"
TRUE_STRING = "true"
FALSE_STRING = "false"

MONITOR_SYMBOL = "\\"

REGEX_DELETING_PATTERN = r"^[\{\[]\n\t*|\t*[\}\]]$"


class JSON(ISerializer):
    """
    Custom JSON-serializer
    """

    def _check_value_end(self, ch: str, temp: str) -> bool:
        return ch == '"' and len(temp) > 0 and temp[-1] != MONITOR_SYMBOL

    def _serialize_dict(self, object: dict, tab_count=0) -> str:
        result = ""
        TABS = '\t' * tab_count
        for k, v in object.items():
            result += f'{TABS}"{k}": {self._serialize_object(v, tab_count=tab_count + 1)},\n'
        return "{\n" + result.rstrip(",\n") + "\n" + TABS + "}"

    def _serialize_object(self, object: Any, tab_count=0) -> str:
        object_type = type(object)

        if object_type is dict:
            return self._serialize_dict(object, tab_count=tab_count)

        if object_type is list:
            return self._serialize_list(object, tab_count=tab_count)

        if object_type is str:
            return '"' + object.replace('"', f'{MONITOR_SYMBOL}"') + '"'

        if object_type in (int, float):
            return str(object)

        if object_type is type(None):
            return NONE_STRING

        if object_type is bool:
            return TRUE_STRING if object else FALSE_STRING

        raise TypeError(f"Unknown type {object_type}")

    def _serialize_list(self, object: list, tab_count=0) -> str:
        result = ""
        TABS = '\t' * tab_count
        for item in object:
            result += f"{TABS}{self._serialize_object(item, tab_count=tab_count + 1)},\n"

        return "[\n" + result.rstrip(",\n") + "\n" + TABS + "]"

    def _deserialize_dict(self, str: str) -> dict:
        str = re.sub(REGEX_DELETING_PATTERN, "", str).strip()
        result = {}
        is_key = True
        key = None
        tmp = ""
        char_index = 0
        string_len = len(str)
        brace_count = 0
        bracket_count = 0
        while char_index < string_len:
            ch = str[char_index]
            if is_key:
                if self._check_value_end(ch, tmp):
                    key = tmp + ch

                    tmp = ""
                    is_key = False
                    char_index += 1  # skip ":"
                else:
                    tmp += ch
            else:
                if brace_count == bracket_count == 0 and (
                    (
                        tmp.lstrip().startswith('"') and
                        self._check_value_end(ch, tmp)
                    ) or
                    (
                        not tmp.startswith('"') and
                        ch == ','
                    )
                ):
                    tmp = tmp + ch
                    result[self._deserialize_object(
                        key)] = self._deserialize_object(tmp.strip().rstrip(','))
                    tmp = ""
                    is_key = True
                    # find next key start index
                    char_index = str.find('"', char_index + 1) - 1
                    if char_index < 0:
                        break
                else:
                    if ch == '{':
                        brace_count += 1
                    if ch == '[':
                        bracket_count += 1
                    if ch == ']':
                        bracket_count -= 1
                    if ch == '}':
                        brace_count -= 1
                    tmp += ch
            char_index += 1
        if tmp.strip() != "":
            result[self._deserialize_object(
                key)] = self._deserialize_object(tmp.strip())
        return result

    def _deserialize_list(self, str: str) -> list:
        str = re.sub(REGEX_DELETING_PATTERN, "", str)
        result = []
        tmp = ""
        char_index = 0
        string_len = len(str)
        brace_count = 0
        bracket_count = 0
        while char_index < string_len:
            ch = str[char_index]
            if brace_count == bracket_count == 0 and (
                (
                    tmp.startswith('"') and
                    self._check_value_end(ch, tmp)
                ) or
                (
                    not tmp.startswith('"') and
                    ch == ','
                )
            ):
                tmp = tmp + ch
                result.append(self._deserialize_object(
                    tmp.strip().rstrip(',')))
                tmp = ""
                char_index = str.find(',', char_index)
                if char_index < 0:
                    break
            else:
                if ch == '{':
                    brace_count += 1
                if ch == '[':
                    bracket_count += 1
                if ch == ']':
                    bracket_count -= 1
                if ch == '}':
                    brace_count -= 1
                tmp += ch
            char_index += 1
        if tmp.strip() != "":
            result.append(self._deserialize_object(tmp.strip().rstrip(',')))
        return result

    def _deserialize_object(self, str: str) -> Any:
        if str.startswith("{"):
            return self._deserialize_dict(str)

        if str.startswith("["):
            return self._deserialize_list(str)

        if str.startswith('"'):
            return str.strip('"').replace(f'{MONITOR_SYMBOL}', '')

        if str == NONE_STRING:
            return None

        if str == TRUE_STRING:
            return True

        if str == FALSE_STRING:
            return False

        if str.find(".") != -1:
            return float(str)

        return int(str)




    def dump(self, obj: Any, fp: IO) -> None:
        fp.write(self._serialize_object(obj))

    def dumps(self, obj: Any) -> str:
        return self._serialize_object(obj)

    def load(self, fp: IO) -> dict:
        return self._deserialize_object(fp.read())

    def loads(self, s: str) -> dict:
        return self._deserialize_object(s)
