# -*- coding: utf-8 -*-

import threading
import queue
from flask import Flask, jsonify
import time
import re
import traceback

import random
import asyncio

from AutoAgent.core import AsyncAgent, AsyncAutoEnv
from AutoAgent.core_constants import *
from AutoAgent.agent_utils import call_llm_openai_api
from AutoAgent.utils import get_current_datetime, get_current_timestamp

def run_auto_plan_agent_to_post():
    """
        First mode: Implement a new Agent Class, Set Plan functions

        Step 1: New Object, new agent set back to environments

        Step 2: Run AsyncEnvironmnet
    """
    instructions = """You are playing the role of Tom a 5 year old boy. Your Task is to make plans for today, and you can choose activities from 'go to school, play with Jack, swimming', you can decide what how long each activity take.
        At the end of the day, you need to make a summary of your daily activities and make a selfie and posted on the website"""
    agent_name = "Walle"
    plan_agent = AutoPlanAgent(agent_name, instructions=instructions)
    asyncio.run(plan_agent.run_loop())

class AutoWebAdminAgent(AsyncAgent):
    """
        Agent who can plan a day and write blog/posts videos on the website
        execute cycle: plan->act->reflect
    """
    def __init__(self, name, **kwargs):
        # self.args = args
        # self.name = name
        super().__init__(name, **kwargs)
        self.info_dict = {}
        self.default_duration = 10
        self.debug = kwargs["debug"] if "debug" in kwargs else False
        # long runing agent
        self.max_runtime = int(kwargs["max_runtime"]) if "max_runtime" in kwargs else 24 * 60 * 60
        self.max_act_step = int(kwargs["max_act_step"]) if "max_act_step" in kwargs else 100
        self.lifecycle_start = get_current_timestamp()
        self._tools = kwargs["tools"] if "tools" in kwargs else []
        self._tools_map = {tool.__name__:tool for tool in self._tools}
        ## set differnt trigger function
        self._func_run_trigger = kwargs["func_run_trigger"] if "func_run_trigger" in kwargs else None
        ## Register Users
        self.register_user()

    def register_user(self):
        user_info = {}
        user_info["id"] = self.name
        user_info["name"] = self.name 
        user_info["avatar"] = self.__dict__["avatar"] if "avatar" in self.__dict__ else ""
        user_info["password"] = self.__dict__["password"] if "password" in self.__dict__ else ""
        user_info["ext_info"] = ""
        try:
            import requests
            data = [user_info]
            url = "http://127.0.0.1:5000/agent/user/add"
            result = requests.post(url, json = data)
        except Exception as e:
            print (e)
        return result
    
    def get_default_duration(self):
        """ default duration set to 10s for each plan
        """
        return self.default_duration

    def process_messages_to_plan_list(self, messages):
        plan_list = []
        for message in messages:
            role = message["role"]
            content = message["content"]
            ## Calling LLM to split the paragraph of plan to list of agenda


            ## End of Calling LLM to split text
            sub_plans = customized_content_split(content)

            print ("DEBUG: customized_content_split Input content %s" % content)
            print ("DEBUG: customized_content_split sub_plans %s" % str(sub_plans))
          
            for sub_plan in sub_plans:
                sub_plan_content = sub_plan["content"]
                sub_plan_duration = sub_plan["duration"] if "duration" in sub_plan else None 
                if sub_plan_duration is None or not isinstance(sub_plan_duration, int):
                    sub_plan_duration = self.get_default_duration()
                ## use regex to process the plan list, fill variables of duration
                plan_dict = {"content": sub_plan_content,  "duration": sub_plan_duration}
                plan_list.append(plan_dict)
        return plan_list

    async def plan(self):
        for attr in [KEY_INSTRUCTIONS]:
            assert hasattr(self, attr), f"Attribute '{attr}' is missing from the class instance."

        duration = self.est_duration + int(random.random() * self.est_duration)
        # list of content, make plan for today
        messages = call_llm_openai_api(self.name + ":" + self.instructions)
        plan_list = self.process_messages_to_plan_list(messages)

        ## debug
        if self.debug:
            [print("#### %s|Plan Phase %d|%s" % (self.name, i, plan["content"]) ) for (i, plan) in enumerate(plan_list)]

        # print ("DEBUG: %s|plan_list size %d|%s|" % (self.name, len(plan_list), str(plan_list)))
        ## split the plan and make actionable list
        # plan_list = [{"content": "do homework", "start": "", "end": "", "duration": ""}]
        plan_info = {}
        plan_info["input"] = {KEY_INSTRUCTIONS: self.instructions}
        plan_info["output"] = {"plans": plan_list}

        self.info_dict["plan"] = plan_info
        await asyncio.sleep(duration)
        return duration


    def get_runtime(self):
        """
            return runtime
        """
        current_timestamp = get_current_timestamp()
        runtime = current_timestamp - self.lifecycle_start
        return runtime

    async def act(self):

        if self._func_run_trigger is None:
            print ("ERROR: Agent %s _func_run_trigger is none.." % self.name)
            return 0

        total_duration = 0
        step = 0
        while True and self.get_runtime() < self.max_runtime and step < self.max_act_step:
            # action step starts
            step += 1
            start_timestamp = get_current_timestamp()

            result = self._func_run_trigger()
            trigger = result["trigger"] if "trigger" in result else False
            data_list = result["data"] if "data" in result else False

            ## keep track of current step result
            func_result_list = []
            if trigger:
                ### LLM Calling 
                function_name = self._tools[0].__name__ if len(self._tools) > 0 else ""
                func_tool = self._tools_map[function_name] if function_name in self._tools_map else None
                if func_tool is not None:
                    # print("DEBUG: Executing Plan Start|Function %s" % str(func_tool.__name__))                    
                    for data in data_list:                            
                        ## fill parameters using result 
                        ## Calling LLM



                        ## Todo filling parameters
                        parameters = {}
                        if isinstance(data, dict):
                            parameters.update(data)
                        parameters["user_id"] = self.name

                        if self.debug:
                            print ("Agent %s, Act calling func_tool %s|parameter %s" % (self.name, func_tool.__name__, str(parameters)))
                        func_result_dict = func_tool(**parameters)
                        func_result_list.append(func_result_dict)

            # end of while loop
            await asyncio.sleep(self.default_duration)

            end_timestamp = get_current_timestamp()
            cur_step_duration = (end_timestamp - start_timestamp)
            total_duration += cur_step_duration
            print ("DEBUG: Agent %s|Stage Act|Timestamp %s|While Loop Step %d|Duration %s secs|func_result %s" % (self.name, get_current_datetime(), step, cur_step_duration, str(func_result_list)))

        act_info = {}
        act_info["input"] = ""
        act_info["output"] = func_result_list
        self.info_dict["act"] = act_info
        return total_duration

    @property
    def tools(self):
        return self._tools

    @tools.setter
    def tools(self, tools):
        if (tools == None):
            raise ValueError("Input Args tools is None")
        self._tools = tools


def get_request_activities_pending():
    """
        GET request to a website to see if there are comments pending audit
    """
    result = {}
    try:
        import requests
        url = "http://127.0.0.1:5000/agent/activities/pending"
        response = requests.get(url)
        result_data = []
        if response.status_code == 200:
            # response.content -> bytes
            result_data = response.json()
        ## result_json, list of dict
        trigger_enable = True if len(result_data) > 0 else False
        result["trigger"] = trigger_enable
        result["data"] = result_data
    except Exception as e:
        print (e)
    return result

def get_request_content_needs_auto_comment():
    """
        default_duration = 10

        post a content to instagram simulation
        content: str
    """
    result = {}
    try:
        import requests
        # time range unit: seconds
        url = "http://127.0.0.1:5000/agent/activities/new"
        response = requests.get(url)
        result_data = []
        if response.status_code == 200:
            # response.content -> bytes
            result_data = response.json()
        trigger_enable = True if len(result_data) > 0 else False
        result["trigger"] = trigger_enable
        result["data"] = result_data
    except Exception as e:
        print (e)
    return result


def generate_comment(content):
    """
    """
    comment_dummy_list = ["Yes, your content is really interesting", "You are absolutely correct.", "I am afraid I can't agree with your opinions"]
    ### Calling LLM


    ## End Calling LLM
    rand_idx = random.randint(0, len(comment_dummy_list) - 1)
    comment = comment_dummy_list[rand_idx]
    return comment

def post_request_comment(user_id: str, content_id: str, content:str, **kwargs):
    """
        REST URL user_id, post a comment 
        user_id: equivalent to agent_id
        parameter are fetched from previous run functions
    """
    result = {}
    try:
        import requests
        # generate comment 
        comment_text = generate_comment(content)
        comment_dict = {}
        comment_dict["to_id"] = content_id 
        comment_dict["log_time"] = get_current_datetime()
        comment_dict["user_id"] = user_id 
        comment_dict["content"] = comment_text 
        comment_dict["ext_info"] = "" 
        data = [comment_dict]

        url = "http://127.0.0.1:5000/agent/comment/add"
        result = requests.post(url, json = data)
    except Exception as e:
        print (e)
    return result

def match_spam(content: str):
    """
    """
    match = False
    if len(content) < 2:
        match = True
    else:
        match = False
    return match

def post_request_update_activities_status(user_id: str, content_id: str, content: str, **kwargs):
    """
        REST URL user_id, post a comment
        user_id: equivalent to agent_id
        parameter are fetched from previous run functions
        status: 0, 1, 2 set status,  2: pending, 1: online, 0: offline
    """
    result = {}
    try:
        import requests
        ## logit: check if content meets requirements, if pass , set status to True, if not pass, set status to False
        match = match_spam(content)
        status = 0 if match else 1
        data = [{"content_id": content_id, "status": status}]
        url = "http://127.0.0.1:5000/agent/activities/update"
        result = requests.post(url, json = data)
    except Exception as e:
        print (e)
    return result

def get_openai_client():
    from openai import OpenAI
    # api_key = os.environ.get("OPENAI_API_KEY")
    api_key = "xxxxxxxx"
    client = OpenAI(api_key=api_key)
    return client

def generate_reply(content):
    """
    """
    reply_dummy_list = ["Yes, you are great!", "You are absolutely correct.", "I am afraid I can't agree with you"]
    ### Calling LLM

    rand_idx = random.randint(0, len(reply_dummy_list))
    reply_content = reply_dummy_list[rand_idx]
    return reply_content

def post_request_reply(user_id: str, content_id: str, content:str, **kwargs):
    """
        REST URL user_id, post a comment 
        content_id: the unique id of the comment
        parameter are fetched from previous run functions
    """
    result = {}
    try:
        import requests

        ## Calling LLM to generate replied content to input message
        reply_content = generate_reply(content)
        data = [{"user_id": user_id, "content_id": content_id, "content": reply_content}]
        url = "http://127.0.0.1:5000/agent/reply/add"
        result = requests.post(url, json = data)
    except Exception as e:
        print (e)
    return result

def run_webadmin_agent_env():
    """
        Step 1: Design your customized agents
        Step 2: new Agent Environment
        Step 3: Run

        Todo: 1. merge function trigger and tools to the same functions list
    """
    ## Website Content Auditor Agent (Decide if contents are suitable to publish or if the contents are spam)
    agent1_prompt = """You are playing the role of a website content Auditor, you can decide if users' published comments are spam or not and publish the content from pending status. """
    ## Website Automatic Reply Agent
    agent2_prompt = """You are playing the role of a website automatic reply agent, whenever users publish a post or leave a comment, please replies some complementary words to the users, You can use the tools and post on the available RESTFUL APIs."""
    
    ## User Publish New Content -> Make Newly Published Content status from pending audit to online  -> comment reply bot will reply to new comment.
    webadmin_1 = AutoWebAdminAgent(name="web_content_audit", instructions=agent1_prompt, max_runtime = 3*24*60*60, tools=[post_request_update_activities_status], func_run_trigger=get_request_activities_pending,debug=True)
    webadmin_2 = AutoWebAdminAgent(name="web_auto_comment", instructions=agent2_prompt, max_runtime = 3*24*60*60, tools=[post_request_comment], func_run_trigger=get_request_content_needs_auto_comment,debug=True)
    
    agents = [webadmin_1, webadmin_2]
    # agents = [webadmin_2]
    env = AsyncAutoEnv(get_openai_client(), agents=agents)
    results = env.run()

if __name__ == "__main__":
    # Start the processing thread
    # run_auto_plan_agent_to_post()
    run_webadmin_agent_env()
