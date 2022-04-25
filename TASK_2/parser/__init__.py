import sys
import imp
import inspect
from abc import ABC, abstractmethod
from typing import IO, Any, Union
from types import FunctionType, BuiltinFunctionType, CodeType, GetSetDescriptorType, MappingProxyType, MethodDescriptorType, ModuleType, WrapperDescriptorType, CellType
from .constants import BYTES_TYPE_STRING, CODE_TYPE_STRING, FUNCTION_TYPE_STRING, CLASS_TYPE_STRING, INSTANCE_TYPE_STRING, MODULE_TYPE_STRING


def _f(): pass


class ISerializer(ABC):
    @abstractmethod
    def dump(self, obj: dict, fp: IO) -> None:
        ...

    @abstractmethod
    def dumps(self, obj: dict) -> str:
        ...

    @abstractmethod
    def load(self, fp: IO) -> dict:
        ...

    @abstractmethod
    def loads(self, s: str) -> dict:
        ...


def is_std_lib_module(module: ModuleType) -> bool:
    python_libs_path = sys.path[2]
    module_path = imp.find_module(module.__name__)[1]
    return (
        module.__name__ in sys.builtin_module_names or
        python_libs_path in module_path or
        'site-packages' in module_path
    )


class ComplexSerializer():
    """
    Serialize complex object types such as class, object, function
    """

    def __init__(self, serializer: ISerializer, test_obj=None) -> None:
        self._serializer = serializer

        if test_obj is not None:
            self.t = self._deserialize_object(self._serialize_object(test_obj))

    def _serialize_code(self, code: CodeType) -> dict:
        result = {}
        for k, v in inspect.getmembers(code):
            if not k.startswith("co"):
                continue
            result[k] = self._serialize_object(v)
        return result

    def _serialize_function(self, fun: FunctionType) -> dict:
        result = {
            "__name__": fun.__name__,
            "__globals__": {},
            "__code__": {},
            "__closure__": []
        }
        function_code = fun.__code__
        function_globals = fun.__globals__
        function_closure = fun.__closure__
        result["__code__"].update(self._serialize_code(function_code))
        for k, v in function_globals.items():
            if (k in __builtins__ or
                    k in (
                        "__builtins__", "__cached__", "__file__"
                    )
                ):
                continue
            if k == fun.__name__:
                global_value = fun.__name__
            elif inspect.isclass(v):
                global_value = "CLASS"
            else:
                global_value = self._serialize_object(v)
            if global_value is not None:
                result["__globals__"][k] = global_value
        if function_closure is not None:
            for cell in function_closure:
                cell_content = cell.cell_contents
                if inspect.isclass(cell_content):
                    result["__closure__"].append(cell_content.__name__)
                else:
                    result["__closure__"].append(
                        self._serialize_object(cell_content))

        return result

    def _serialize_class(self, _class: type) -> dict:
        result = {
            "__name__": _class.__name__,
            "members": {}
        }
        if _class == type:
            result["__bases__"] = []
        else:
            result["__bases__"] = [self._serialize_class(
                base) for base in _class.__bases__ if base != object]
            for member in inspect.getmembers(_class):
                if member[0] not in (
                        "__mro__", "__base__", "__basicsize__",
                        "__class__", "__dictoffset__", "__name__",
                        "__qualname__", "__text_signature__", "__itemsize__",
                        "__flags__", "__weakrefoffset__", "__objclass__"
                    ) and type(member[1]) not in (
                        WrapperDescriptorType,
                        MethodDescriptorType,
                        BuiltinFunctionType,
                        MappingProxyType,
                        GetSetDescriptorType
                ):
                    result["members"][member[0]
                                      ] = self._serialize_object(member[1])
        return result

    def _serialize_object(self, obj: Any) -> dict:
        result = {}
        obj_type = type(obj)
        if obj_type == dict:
            for name, value in obj.items():
                if(inspect.isbuiltin(value)):
                    continue
                result[name] = self._serialize_object(value)

        elif obj_type == list or obj_type == tuple:
            result = []

            for value in obj:
                result.append(self._serialize_object(value))


        elif isinstance(obj, CodeType):
            result["type"] = CODE_TYPE_STRING
            result["value"] = self._serialize_code(obj)

        elif inspect.ismodule(obj):
            result["type"] = MODULE_TYPE_STRING
            result["value"] = self._serialize_module(obj)

        elif obj_type == bytes:
            result["type"] = BYTES_TYPE_STRING
            result["value"] = list(obj)

        elif inspect.isroutine(obj):
            result["type"] = FUNCTION_TYPE_STRING
            result["value"] = self._serialize_function(obj)


        elif isinstance(obj, (int, float, bool, str)) or obj is None:
            return obj

        elif inspect.isclass(obj):
            result["type"] = CLASS_TYPE_STRING
            result["value"] = self._serialize_class(obj)

        else:
            result["type"] = INSTANCE_TYPE_STRING
            result["value"] = self._serialize_instance(obj)
        return result

    def _serialize_module(self, module: ModuleType) -> dict:
        result = {
            "__name__": module.__name__,
        }
        if is_std_lib_module(module):
            return result
        result["members"] = {}
        for k, v in inspect.getmembers(module):
            if k.startswith("__"):
                continue
            result["members"][k] = self._serialize_object(v)
        return result

    def _serialize_instance(self, instance: Any) -> dict:
        result = {
            "class": self._serialize_class(instance.__class__),
            "members": {}
        }
        for k, v in inspect.getmembers(instance):
            if k.startswith("__") or inspect.isroutine(v):
                continue
            result["members"][k] = self._serialize_object(v)
        return result

    def _deserialize_object(self, obj: Any) -> Any:
        obj_type = type(obj)
        if(obj_type == list):
            return tuple(self._deserialize_object(i) for i in obj)
        if(obj_type != dict):
            return obj
        obj_type = obj["type"]
        obj_value = obj["value"]
        if obj_type is not None:
            if obj_type == FUNCTION_TYPE_STRING:
                return self._deserialize_function(obj_value)

            if obj_type == CLASS_TYPE_STRING:
                return self._deserialize_class(obj_value)

            if obj_type == INSTANCE_TYPE_STRING:
                return self._deserialize_instance(obj_value)

            if obj_type == BYTES_TYPE_STRING:
                return bytes(obj_value)

            if obj_type == CODE_TYPE_STRING:
                return self._deserialize_code(obj_value)

            if obj_type == MODULE_TYPE_STRING:
                return self._deserialize_module(obj_value)
        result = {}
        for name, object in obj.items():
            result[name] = self._deserialize_object(object)
        return result

    def _deserialize_code(self, code_dict: dict) -> CodeType:
        function_code = {}
        for k, v in code_dict.items():
            function_code[k] = self._deserialize_object(v)
        return _f.__code__.replace(**function_code)

    def _deserialize_module(self, module_dict: dict) -> ModuleType:
        module_name = module_dict["__name__"]
        if "members" not in module_dict:
            return __import__(module_name)
        module = imp.new_module(module_name)
        for k, v in module_dict["members"].items():
            setattr(module, k, self._deserialize_object(v))
        return module

    def _deserialize_function(self, function_dict: dict, _class=None) -> FunctionType:
        function_name = function_dict["__name__"]

        function_globals = {}
        for k, v in function_dict["__globals__"].items():
            function_globals[k] = self._deserialize_object(v)
        function_closure = tuple()
        for closure_member in function_dict["__closure__"]:
            if type(closure_member) is str and _class.__name__ == closure_member:
                function_closure += (CellType(_class), )
            else:
                function_closure += (CellType(closure_member), )
        function = FunctionType(
            self._deserialize_code(function_dict["__code__"]),
            function_globals,
            name=function_name,
            closure=function_closure
        )
        function.__globals__["__builtins__"] = __import__("builtins")
        if function_name in function_globals:
            function.__globals__[function_name] = function
        return function

    def _deserialize_instance(self, instance_dict: dict) -> Any:
        instance_class = self._deserialize_class(instance_dict["class"])
        instance_members = {}
        for k, v in instance_dict["members"].items():
            instance_members[k] = self._deserialize_object(v)
        obj = object.__new__(instance_class)
        obj.__dict__ = instance_members
        return obj

    def _deserialize_class(self, class_dict: dict) -> type:
        class_name = class_dict["__name__"]
        class_bases = tuple(self._deserialize_class(base)
                            for base in class_dict["__bases__"])
        class_methods = {}
        if len(class_bases) == 0:
            class_bases = ()
        class_info = {}
        for member_key, member_value in class_dict["members"].items():
            if member_key in ("__name__", "__bases__"):
                continue
            if type(member_value) is dict and member_value["type"] == FUNCTION_TYPE_STRING:
                class_methods[member_key] = member_value["value"]
            else:
                class_info[member_key] = self._deserialize_object(member_value)
        _class = type(class_name, class_bases, class_info)
        for method_name, method_value in class_methods.items():
            setattr(_class, method_name, self._deserialize_function(
                method_value, _class=_class))
        return _class


    def dump(self, obj, fp: IO) -> None:
        return self._serializer.dump(self._serialize_object(obj), fp)

    def dumps(self, obj) -> str:
        return self._serializer.dumps(self._serialize_object(obj))

    def load(self, fp: IO):
        return self._deserialize_object(self._serializer.load(fp))

    def loads(self, s: str):
        return self._deserialize_object(self._serializer.loads(s))
