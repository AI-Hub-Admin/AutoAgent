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

def get_openai_client():
    from openai import OpenAI
    # api_key = os.environ.get("OPENAI_API_KEY")
    api_key = "xxxxxxxx"
    client = OpenAI(api_key=api_key)
    return client

def run_async_agents_env():
    """
    """
    ## Website Content Auditor Agent (Decide if contents are suitable to publish or if the contents are spam)
    agent1_prompt = """You are playing the role of a web admin agent... """
    ## Website Automatic Reply Agent
    agent2_prompt = """You are playing the role of a automatic reply agent..."""
    ## User Publish New Content -> Make Newly Published Content status from pending audit to online  -> comment reply bot will reply to new comment.
    agent_1 = AsyncAgent(name="agent 1", instructions=agent1_prompt)
    agent_2 = AsyncAgent(name="agent 2", instructions=agent2_prompt)

    agents = [agent_1, agent_2]
    env = AsyncAutoEnv(get_openai_client(), agents=agents)
    results = env.run()

if __name__ == "__main__":
    run_async_agents_env()
