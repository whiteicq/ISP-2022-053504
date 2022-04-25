"""
Utility for encoding your python classes, objects, functions
"""

import argparse
import re
import sys
from parser import ComplexSerializer, ISerializer
from serializers.json import JSON
from serializers.toml import TOML
from serializers.yaml import YAML
from test_module import _t

sys.path.insert(0, ".")


def _get_serializer_by_string(str: str) -> ISerializer:
    if str == "json":
        return JSON

    if str == "toml":
        return TOML

    if str == "yaml":
        return YAML

    raise TypeError("Unknown serializer type")


if __name__ == "__main__":
    print("Hello")
    argpars = argparse.ArgumentParser()
    argpars.add_argument("source", type=str, help="Path to source file")
    argpars.add_argument("format", type=str, help="Serialize format(json, toml or yaml) for result")
    argpars.add_argument("-r", "--result-file", type=str, help="Path to result file. If not exist, it will be created")
    namespace = argpars.parse_args()
    result_format = namespace.format
    source_path = namespace.source
    source_format = re.search(r"\w+$", source_path).group()
    if source_format == result_format:
        print("Same type")
        exit()
    source_serializer = ComplexSerializer(
        _get_serializer_by_string(source_format)())
    result_serializer = ComplexSerializer(
        _get_serializer_by_string(result_format)())
    with open(source_path) as file:
        object = source_serializer.load(file)
        if namespace.result_file is not None:
            with open(namespace.result_file, "w") as output_file:
                result_serializer.dump(object, output_file)
        else:
            print(
                result_serializer.dumps(object)
            )
