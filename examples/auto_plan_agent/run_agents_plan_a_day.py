# -*- coding: utf-8 -*-

import threading
import queue
from flask import Flask, jsonify
import time
import re
import os

import random
import asyncio
import json

from AutoAgent.core import AsyncAgent, AsyncAutoEnv
from AutoAgent.core_constants import *
from AutoAgent.agent_utils import call_llm_openai_api
from AutoAgent.utils import get_current_datetime, get_current_timestamp, read_file

## fine a tool to post autoagent activity to agentboard
def post_agent_activity(role:str, content:str, name: str, log_time: str):
    """
        post a content to agentboard
        URI: http://127.0.0.1:5000/agent/activities
    """
    result = {}
    try:
        import requests
        data = [{"role": role, "content": content, "name": name, "log_time": log_time}]
        url = "http://127.0.0.1:5000/agent/activities"
        result = requests.post(url, json = data)
    except Exception as e:
        print (e)
    return result


## Plan Agent to Post Activities
tools = [post_agent_activity]
tools_map = {tool.__name__:tool for tool in tools}


datatime_regex = r"(\d{1,2}:\s?\d{2}\s?(AM|PM)\s-\s\d{1,2}:\s?\d{2}\s?(AM|PM))"

def split_paragraph(text):
    """
        split raw text return by openai
        
    """
    # para_sep = "\n\n"
    # para_highlight_sep = "\n**\n"
    # text_norm = text.replace(para_sep, para_highlight_sep)
    # para_list = text.split(para_sep)
    para_sep = r'[\r\n]+'
    para_list = re.split(para_sep, text)
    return para_list

def customized_content_split(text):
    """ Split text into list of plans
    """
    plan_list = []
    cur_plan_dict = {}
    cur_slot = ""
    cur_content = ""
    cur_duration = ""

    paragraph_list = split_paragraph(text)
    for para_text in paragraph_list:
        para_text_time_split = re.split(datatime_regex, para_text)
        for paragraph in para_text_time_split:
            if paragraph in ("AM", "PM"):
                continue
            if re.match(datatime_regex, paragraph):
                ## add new
                if cur_content != "":
                    ## process content
                    content = cur_slot + " " + cur_content
                    content = content.strip()
                    ## Todo: process duration
                    duration = ""
                    cur_plan_dict = {"duration": duration, "content": content}
                    plan_list.append(cur_plan_dict)
                cur_slot = paragraph
                cur_content = ""
            else:
                cur_content = cur_content + paragraph
    # append last activity
    content = cur_slot + " " + cur_content
    content = content.strip()
    ## Todo: process duration
    duration = ""    
    cur_plan_dict = {"duration": duration, "content": content}
    plan_list.append(cur_plan_dict)    
    return plan_list

def unittest_customized_content_split():
    """
        OpenAI ** split paragraph
    """
    text1 = """
            Tom's Day Plan 🎉8:00 AM - 12:00 PM: Go to School 🏫 I’ll go to school in the morning! We have story time, snack time, and maybe even some painting. I’ll get to play with my friends at recess too! Time: 4 hours 1: 00 PM - 2: 00 PM: Play with Jack🧩 After lunch,I’ m going to play with my best friend, Jack!We’ ll go to the park and play on the swings, maybe play some tag or hide and seek.⏰Time: 1 hour 3: 00 PM - 4: 00 PM: Swimming🏊‍♂️ In the afternoon, I’ ll go swimming!I love splashing in the pool and practicing my float.I’ m getting better at my doggy paddle!⏰Time: 1 hour Summary of My Day!🌟Today, I went to school, played with my friend Jack, and went swimming.It was super fun!I did so many things, and I can’ t wait to do it all again tomorrow.📸Selfie for the website🖼️ 
        """
    plan_list_1 = customized_content_split(text1)
    print (plan_list_1)

    text2 = """
        Morning: Start with breakfast to fuel up for the day. \n\n Mid-morning to Afternoon: Head to the company, then arrange meetings with clients as needed. I’ll keep an eye on the clock to ensure everything wraps up in time. \n\n 5:00 pm: Pick up Tom from school. \n\n Evening: End the day by taking a picture with Tom to share with Lily, so she sees her two favorite guys together. This should keep the day smooth and still make time for a special moment with Tom at the end!
    """
    plan_list_2 = customized_content_split(text2)
    print (plan_list_2)

def parse_time(time_str):
    """
    """
    match = re.match(r'(\d{1,2}):(\d{2})', time_str)
    if match:
        hour, minute = match.groups()
        return int(hour), int(minute)
    return None

class AutoPlanAgent(AsyncAgent):
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
        self.register_user()
        # restore memory if new memory are provided
        memory = kwargs["memory"] if "memory" in kwargs else None
        if memory is not None:
            self.restore_memory(memory)

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
            print ("ERROR: Agent register_user failed...")
            print (e)

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

            # print ("DEBUG: customized_content_split Input content %s" % content)
            # print ("DEBUG: customized_content_split sub_plans %s" % str(sub_plans))

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
        messages = []
        key = os.environ.get("OPENAI_API_KEY")
        if key is not None:
            messages = call_llm_openai_api(self.name + ":" + self.instructions)
        else:
            messages = self.memory

        # messages = call_llm_openai_api(self.name + ":" + self.instructions)
        plan_list = self.process_messages_to_plan_list(messages)

        ## debug
        if self.debug:
            [print("#### %s|Plan Phase %d|%s" % (self.name, i, plan["content"]) ) for (i, plan) in enumerate(plan_list)]

        plan_info = {}
        plan_info["input"] = {KEY_INSTRUCTIONS: self.instructions}
        plan_info["output"] = {"plans": plan_list}
        self.info_dict["plan"] = plan_info
        await asyncio.sleep(duration)
        return duration

    async def act(self):
        max_duration = 5
        duration = self.est_duration + int(random.random() * self.est_duration)

        # get output from previous nodes
        plan_dict = self.info_dict["plan"] if "plan" in self.info_dict else {}
        plan_output = plan_dict["output"] if "output" in plan_dict else []
        plan_list = plan_output["plans"] if "plans" in plan_output else []

        result_dict = {}
        plan_id = 0

        total_duration = 0
        for plan in plan_list:
            plan_id += 1
            
            # act according to the plan
            plan_content = plan["content"] if "content" in plan else ""
            plan_duration = plan["duration"] if "duration" in plan else self.get_default_duration()
            if plan_content == "":
                continue

            ## acting simulation
            assert isinstance(plan_duration, int), "planned duration is int..."

            print ("### %s|%s|Act Sub Plan %d|Sub Plan Duration %d" % (self.name, get_current_datetime(), plan_id, plan_duration))

            total_duration += plan_duration
            await asyncio.sleep(plan_duration)

            function_name = post_agent_activity.__name__
            func_tool = tools_map[function_name]
            parameters = {}

            ## run time and plan estimated time 
            parameters["role"] = "assistant"
            parameters["content"] = plan_content
            parameters["name"] = self.name
            parameters["log_time"] = get_current_datetime()

            # print("DEBUG: Executing Plan Start|Function %s" % str(func_tool.__name__))
            result = func_tool(**parameters)
            # print("DEBUG: Executing Plan End|Result is %s" % str(result))
            result_dict[plan_id] = result

        act_info = {}
        act_info["input"] = ""
        act_info["output"] = result_dict
        self.info_dict["act"] = act_info
        return total_duration

def get_openai_client():
    from openai import OpenAI
    # api_key = os.environ.get("OPENAI_API_KEY")
    api_key = "xxxxxxxx"
    client = OpenAI(api_key=api_key)
    return client

def run_auto_plan_agent_to_post():
    """
        Run Case: Initialize an AutoPlan Agent who can make plans and post the plans to agentboard locally
    """
    instructions = """You are playing the role of Tom a 5 year old boy. Your Task is to make plans for today, and you can choose activities from 'go to school, play with Jack, swimming', you can decide what how long each activity take.
        At the end of the day, you need to make a summary of your daily activities and make a selfie and posted on the website"""
    agent_name = "Walle"
    plan_agent = AutoPlanAgent(agent_name, instructions=instructions)
    asyncio.run(plan_agent.run_loop())

def run_auto_plan_agent_env():
    """
        Run Case: Initialize two AutoPlan Agents, Tom and Dad, who make plans individually and post their activities on the agentboard 
    """
    agent1_prompt = """You are playing the role of Tom a 5 year old boy. Your Task is to make plans for today, and you can choose activities from 'go to school, play with Jack, swimming', you can decide what how long"
     At the end of the day, you need to make a summary of your daily activities and make a selfie and posted on the website"""
    agent2_prompt = """You are playing the role of Tom's dad and you are making plans for today, you can choose between having breakfast, go to company, 
    have meetings with clients. But at 5:00 pm, you have to pick up tom, your son from school.  At the end of the day, you should take a picture with your boy Tom and send to his mother, Lily."""

    memory_list = [json.loads(line) for line in read_file("./memory.txt")]
    assert len(memory_list) == 2, "Restored 2 agent memories as list of json objects OpenAI response..."

    agent1 = AutoPlanAgent(name="Tom", instructions=agent1_prompt, avatar="icon_children.jpg", memory=[memory_list[0]],debug=True)
    agent2 = AutoPlanAgent(name="Daddy", instructions=agent2_prompt, avatar="icon_male_chat.jpg", memory=[memory_list[1]], debug=True)

    agents = [agent1, agent2]
    env = AsyncAutoEnv(get_openai_client(), agents=agents)
    results = env.run()

if __name__ == "__main__":
    # Start the processing thread
    # run_auto_plan_agent_to_post()
    run_auto_plan_agent_env()
