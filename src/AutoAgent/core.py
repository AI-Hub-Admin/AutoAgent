# -*- coding: utf-8 -*-

import json
import random
import asyncio
import threading
import uuid
import random
import traceback


from .core_constants import *
from .utils import *
from .agent_utils import *

class BaseAgent(object):

    name: str = ""

    def __init__(self, name, **kwargs):
        """
            agent_schema.conf_dict dict of {key, value} pairs
        """
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)
        # self.agent_schema = agent_schema

        # self.config_dict = agent_schema.config_dict
        self.memory = []

    def plan(self, input_dict):
        output_dict={}
        return output_dict

    def act(self, input_dict):
        output_dict={}
        return output_dict

    def reflect(self, input_dict):
        output_dict={}
        return output_dict

    def get(self, key):

        value = None
        if self.agent_schema is not None:
            value = self.agent_schema.get(key)
        else:
            value = None
        return value

### Tools
class BaseTool(object):
    """docstring for ClassName"""

    name: str = ""
    instructions: str = ""

    def __init__(self, name, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def use(self):
        return None

### Async Agent
class AsyncAgent(BaseAgent):
    """
        Async Agent, run with env to storage the parameters
        1. attributes:
            args: list to capture initialization args
            name: str to identify Agent
        2. methods:
    """
    # define attributes for LLM to capture signature
    # args: list   = []
    def __init__(self, name, **kwargs):
        # self.args = args
        # self.name = name
        super().__init__(name, **kwargs)
        # estimated duration of each step
        self.est_duration = 5
        ## internal variable
        self.memory = []
        ## functions to call llm function and process result from llm functions
        self.call_llm = kwargs[KEY_FUNC_CALL_LLM] if KEY_FUNC_CALL_LLM in kwargs else None
        self.process_llm = kwargs[KEY_FUNC_PROCESS_LLM] if KEY_FUNC_PROCESS_LLM in kwargs else None
    
    async def run_loop(self):

        try:
            print ("%s|%s|run_loop start|0" % (self.name, get_current_datetime()))

            plan_duration = await self.plan()
            print ("%s|%s|Plan Complete|%s" % (self.name, get_current_datetime(), plan_duration))

            act_duration = await self.act()
            print ("%s|%s|Act Complete|%s" % (self.name, get_current_datetime(), act_duration))

            reflect_duration = await self.reflect()
            print ("%s|%s|Reflect Complete|%s" % (self.name, get_current_datetime(), reflect_duration))

            total_duration = plan_duration + act_duration + reflect_duration

            return "%s|%s|run_loop complete|%s" % (self.name, get_current_datetime(), total_duration)
        except Exception as e:
            print (e)
            print (traceback.print_exc())
            return "%s|%s|run_loop complete|%s" % (self.name, get_current_datetime(), 0)

    async def plan(self):
        duration = self.est_duration + int(random.random() * self.est_duration)
        await asyncio.sleep(duration)
        return duration

    async def act(self):
        max_duration = 5
        duration = self.est_duration + int(random.random() * self.est_duration)
        await asyncio.sleep(duration)
        return duration

    async def reflect(self):
        duration = self.est_duration + int(random.random() * self.est_duration)
        await asyncio.sleep(duration)
        return duration

    def get_agent_name(self):
        agent_id = str(uuid.uuid4())
        agent_name = "agent %s" % agent_id[0:8]
        return agent_name

class BaseAutoEnv(object):

    # class attributes
    # client = None
    # _agents: list = []
    # _tools: list = []
    # env_prompt: str = ""

    def __init__(self, client, **kwargs):
        """
            client: OpenAI Client or equivalent
            init_dict
        """
        self.client = client
        ##
        # agent_prompt_list = kwargs["KEY_AGENTS"]      # list
        # env_prompt_list = kwargs["env"]               # list
        # tools_prompt_list = kwargs["tools"]           # list
        ## initialize agents
        init_agents = kwargs[KEY_AGENTS] if KEY_AGENTS in kwargs else None
        if init_agents is not None:
            assert isinstance(init_agents, list), "Input param 'agents' should be a list"
            assert len(init_agents) > 0, "Input param init_agents should not be empty list"
            self._agents = init_agents
        else:
            ## initialization from prompt
            agent_prompt_list = kwargs[KEY_AGENTS_PROMPT] if KEY_AGENTS_PROMPT in kwargs else []
            for agent_instruct in agent_prompt_list:
                agent = fill_class_schema(client, AsyncAgent, instructions=agent_instruct)
                print ("# DEBUG: BaseAutoEnv generating agent name %s" % agent.name)
                self._agents.append(agent)

        ## initialize tools
        init_tools = kwargs[KEY_TOOLS] if KEY_TOOLS in kwargs else None
        if init_tools is not None:
            assert isinstance(init_tools, list), "Input param 'tools' should be a list"
            assert len(init_tools) > 0, "Input param 'tools' should not be empty list"
            self._tools = init_tools
        else:
            tools_prompt_list = kwargs[KEY_TOOLS_PROMPT] if KEY_TOOLS_PROMPT in kwargs else []
            for tool_prompt in tools_prompt_list:
                tool = fill_class_schema(client, BaseTool, instructions=tool_prompt)
                self._tools.append(tool)

        ## env_prompt_list -> sys_prompt
        self.env_prompt = kwargs[KEY_ENV_PROMPT] if KEY_ENV_PROMPT in kwargs else ""

    @property
    def agents(self):
        return self._agents

    @agents.setter
    def agents(self, agents):
        if (agents == None):
            raise ValueError("Input Args agents is None")
        self._agents = agents

    @property
    def tools(self):
        return self._tools

    @tools.setter
    def tools(self, tools):
        if (tools == None):
            raise ValueError("Input Args tools is None")
        self._tools = tools

    def run(self, **kwargs):
        return


#### AsyncAutoEnv

def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


class AsyncAutoEnv(BaseAutoEnv):
    """
        Base Asynchronous Autonomous Agents
    """

    def run(self, **kwargs):
        """
            Implement a multi-thread multi-loop of agents running
        """
        num_agents = len(self.agents)

        loops = []
        threads = []
        for i in range(num_agents):
            loop = asyncio.new_event_loop()
            thread = threading.Thread(target=start_event_loop, args=(loop,))
            thread.start()
            loops.append(loop)
            threads.append(thread)

        # Schedule async tasks
        print ("ID|Timestamp|Stage|Duration")
        futures = []
        for loop, agent in zip(loops, self.agents):
            future = asyncio.run_coroutine_threadsafe(agent.run_loop(), loop)
            futures.append(future)

        ## debug
        print ("DEBUG: Futures %s" % str(futures))

        # Gather results from all futures once tasks are complete
        results = [future.result() if future is not None else "" for future in futures]
        print("Results:", results)

        # Stop each event loop after tasks are done
        for loop in loops:
            loop.call_soon_threadsafe(loop.stop)

        # Join all threads
        for thread in threads:
            thread.join()
        return results
