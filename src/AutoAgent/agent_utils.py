#coding=utf-8
#!/usr/bin/python
# @Time    : 2024/11/01
# @Author  : Derek Ding


import os
import inspect
import codecs
import json
from typing import get_type_hints
import traceback

from .core_constants import *

### Agent Function Conversion
def function_to_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }



def function_to_schema_claude(func) -> dict:
    """
        Compatible with Claude's function calling schema
        Ref: 
        https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "name" : func.__name__, 
        "description": (func.__doc__ or "").strip(),
        "input_schema": {
            "type": "object",
            "properties": parameters,
            "required": required
        }
    }


def get_class_attributes_and_signatures(cls):
    attributes = {}    
    # Loop through class attributes using class dictionary
    for name, value in cls.__dict__.items():
        # Get type hint if available
        type_hint = get_type_hints(cls).get(name, "No Type Hint")
        
        # Check if attribute is a function or method
        if inspect.isfunction(value) or inspect.ismethod(value):
            # Get the signature of the function or method
            signature = inspect.signature(value)
            attributes[name] = {
                'type': 'Function/Method',
                'signature': str(signature),
                'type_hint': type_hint
            }
        else:
            # For other attributes, just record the type hint and value type
            attributes[name] = {
                'type': 'Attribute',
                'type_hint': type_hint,
                'value_type': type(value).__name__
            }
    return attributes


def class_to_schema(cls) -> dict:
    """
        Get all the attributes of a cls, including attributes, functions or methods
    """
    
    attributes = get_class_attributes_and_signatures(cls)

    # conver to OpenAI LLM function call format, e.g. AsyncAgent.__init__
    cls_init_method_name = cls.__name__ + "." + INIT_METHOD_NAME


    init_method = attributes[INIT_METHOD_NAME]
    # signature (self, args)
    init_method_signature = init_method["signature"] if "signature" in init_method else {}

    # args list split, key: attribute_name, value: {'type': str}
    parameters = {}
    for pair in attributes.items():
        key = pair[0]
        value = pair[1]
        # filter out all the attributes, exclude all the default attributes of class with __
        if (type(value) is dict) and (value['type'] == 'Attribute') and ("__" not in key):
            type_hint = value['type_hint']
            value_type = value['value_type']
            parameters[key] = {'type': value_type}

    # get required attributes of cls, exclude 'args'
    required = []
    for key in parameters.keys():
        if key != "args":
            required.append(key)

    cls_init_scheme = {
            "type": "function",
            "function": {
                "name": cls_init_method_name,
                "description": (cls.__doc__ or "").strip(),
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required,
                },
            },
        }

    return cls_init_scheme


def execute_tool_call(tool_call, tools_map):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    print(f"Assistant: {name}({args})")
    # call corresponding function with provided arguments
    return tools_map[name](**args)


def execute_tool_call_from_json_simple(tool_call, tools_map):
    """
        tool_call: json format of 
        {'functions': {'name': 'tencent_api_base',
          'parameters': {'arg1': '10',
           'arg2': '20',
           'arg3': '30',
           'arg4': '',
           'arg5': ''}}}

        # 

    """
    name = tool_call["function"]["name"]
    parameters = tool_call["function"]["parameters"]
    # args = json.loads(tool_call.function.arguments)
    print(f"Assistant: {name}({parameters})")
    # call corresponding function with provided arguments
    return tools_map[name](**parameters)

def execute_tool_call_from_json(tool_call, tools_map):
    """
        tool_call: json format of 
        {'functions': {'name': 'tencent_api_base',
          'parameters': {'arg1': '10',
           'arg2': '20',
           'arg3': '30',
           'arg4': '',
           'arg5': ''}}}
        
        ## result distinguish positional args and kwargs
        # 
    """
    name = tool_call["function"]["name"]
    parameters = tool_call["function"]["parameters"]
    # positional argments
    args = parameters["args"] if 'args' in parameters else []
    kwargs = parameters["kwargs"] if 'kwargs' in parameters else {}

    assert type(args) is list
    assert type(kwargs) is dict

    func = tools_map[name]
    result = func(*args, **parameters)
    # args = json.loads(tool_call.function.arguments)
    print(f"Assistant: {name}({args}, {parameters})")
    # call corresponding function with provided arguments
    return result


def execute_cls_init_tool_call_from_json(cls, tool_call, tools_map):
    """
        tool_call: json format of 
        {'functions': {'name': 'tencent_api_base',
          'parameters': {'arg1': '10',
           'arg2': '20',
           'arg3': '30',
           'arg4': '',
           'arg5': ''}}}
        
        ## result distinguish positional args and kwargs
        # init() not returning a new object
    """
    name = tool_call["function"]["name"]
    parameters = tool_call["function"]["parameters"]
    # positional argments
    args = parameters["args"] if 'args' in parameters else []
    kwargs = parameters["kwargs"] if 'kwargs' in parameters else {}

    assert type(args) is list
    assert type(kwargs) is dict

    # func = tools_map[name]
    # result = func(cls, *args, **kwargs)
    result = cls(*args, **kwargs)
    # args = json.loads(tool_call.function.arguments)
    print(f"Assistant: {name}({args}, {parameters})")
    # call corresponding function with provided arguments
    return result


def fill_class_schema(client, cls, **kwargs):
    """ fill prompt into cls schema
        
        cls:
        client: e.g. OpenAI Client
        kwargs: variable key value params

        sample tool call result: '[{"function":{"name":"finance_stock_price_api","parameters":{"symbol_list":["700","1024"],"market":"HK"}}}]'
        
        function: args, **kwargs

        cls init method handle positional args and kwargs argments
    """
    init_method_schema = class_to_schema(cls)

    tool_schemas = [init_method_schema]
    print ("DEBUG: Class Initialization Schema:")
    [print(json.dumps(schema, indent=2)) for schema in tool_schemas]

    # function call for open
    ## construct request
    sys_instruction = "You can fill the function with json format, the schema for the function is %s, the inputs includes %s, please output the executable function values in json format, with key as 'function'"
    prompt_list = []

    parameter_prompt_list = ""
    for key, value in kwargs.items():
        parameter_prompt_list.append("%s=%s" % (str(key), str(value)))
    parameter_prompt = ",".join(parameter_prompt_list)
    for tool in tool_schemas:
        prompt = sys_instruction % (str(tool), parameter_prompt)
        prompt_list.append(prompt)
    final_prompt = "".join(prompt_list)
    print (final_prompt)

    ## save the initialization tools factory
    tools = [cls.__init__]
    init_method_name = cls.__name__ + "." + INIT_METHOD_NAME
    # tools function map, key: str, value: function
    tools_map = {init_method_name: cls.__init__}

    ## calling LLM
    ## start LLM Calling
    # tools_map = {tool.__name__: tool for tool in tools}
    messages = []
    key = os.environ.get(OPENAI_API_KEY)
    if key is not None:
        # set openai variable
        from openai import OpenAI
        from pydantic import BaseModel
        from typing import Optional
        client = OpenAI() 
        response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": final_prompt}],
                    tools=tool_schemas,
                )
        message = response.choices[0].message
        message.tool_calls[0].function

        tool_calls = message.tool_calls
        for tool_call in tool_calls:
            result = execute_tool_call(tool_call, tools_map)
            messages.append(result)
    else:
        openai_tools_call_json_list = input("Please Input the function prompt by LLM: ")
        tool_calls = json.loads(openai_tools_call_json_list)
        
        for tool_call in tool_calls:
            tool_call_result = execute_cls_init_tool_call_from_json(cls, tool_call, tools_map)
            messages.append(tool_call_result)
    # output messages
    print(messages)

    ## fill class with the json
    args = ()
    obj = None
    if len(messages) > 0:
        obj = messages[0]
    ### fill
    return obj

def call_llm_openai_api(prompt):
    """
        Call LLM API if os key is null, load from user_input for debuging

        Reference: https://platform.openai.com/docs/api-reference/introduction

        "content": [
            {
              "type": "text",
              "text": {
                "value": "Hi! How can I help you today?",
                "annotations": []
              }
            }
          ],
    """
    messages = []
    if prompt is None or prompt == "":
        return messages
    try:
        messages = []
        key = os.environ.get("OPENAI_API_KEY")
        if key is not None:
            # set openai variable
            from openai import OpenAI
            from pydantic import BaseModel
            from typing import Optional
            client = OpenAI() 
            response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        tools=[],
                    )
            message = response.choices[0].message
            role = message["role"]
            message_text = message["content"][0]["text"]["value"]
            messages.append({"role": role, "content": message_text})
        else:
            message_json_str = input("Please Input the messages return from LLM:\n")
            if message_json_str == "" or message_json_str is None:
                return messages
            message = json.loads(message_json_str)            
            role = message["role"]
            message_text = message["content"][0]["text"]
            messages.append({"role": role, "content": message_text})
    except Exception as e:
        print (e)
        s = traceback.format_exc()
        print (s)        
    return messages


def test_fill_schema():

    from .core import AsyncAgent
    user_input = """Your name is Tom and you are playing the role of a 5 year old boy. Your Task is to make plans for today, and you can choose activities from 'go to school, play with Jack, swimming', you can decide what how long"
     At the end of the day, you need to make a summary of your daily activities and make a selfie and posted on the website""";
    client = None 
    agent = fill_class_schema(client, AsyncAgent, user_input)
    print ("DEBUG: Agent '%s' initialized is %s" % (agent.name, str(agent)))

def main():
    test_fill_schema()

if __name__ == '__main__':
    main()
