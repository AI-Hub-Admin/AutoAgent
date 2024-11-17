# -*- coding: utf-8 -*-
PROMPT_SEP_HASHTAG = "#"

ROLE_AGENT = "ai"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM_AGENT = "system"
ROLE_HUMAN = "human"

## Action Phase
KEY_INPUT_PLAN = "plan"

## Agent
EMPTY_VALUE = ""
INPUT_KEY_PROMPT = "prompt"
INPUT_KEY_TIMESTAMP = "timestamp"
INPUT_KEY_TIMESLOT = "time_slot"
INPUT_KEY_ACTIVITY = "activity"
INPUT_KEY_PROMPT = "prompt"
INPUT_KEY_INPUT = "input"


KEY_INPUT = "input"
KEY_OUTPUT = "output"
KEY_AGENT_PROMPT ="agent_prompt"
KEY_AGENT_ID = "agent_id"
KEY_AVATAR = "avatar"
KEY_CLASS = "class"


CONFIG_KEY_TASK_TIME = "task_time"
CONFIG_KEY_INTERVAL  = "interval"
CONFIG_KEY_DEBUG  = "debug"
CONFIG_KEY_HUMAN_INTERVENTION = "human_intervention_enable"
CONFIG_KEY_SYS_PROMPT = "sys_prompt"
CONFIG_KEY_HUMAN_PROMPT = "human_prompt"


OUTPUT_KEY_MESSAGES = "messages"
OUTPUT_KEY_AGENT = "agent"

OUTPUT_KEY_ROLE = "role"
OUTPUT_KEY_CONTENT = "content"
OUTPUT_KEY_ID = "id"
OUTPUT_KEY_TIMESTAMP = "timestamp"
OUTPUT_KEY_AVATAR = "avatar"

KEY_INSTRUCTIONS = "instructions"
KEY_AGENTS = "agents"
KEY_AGENTS_PROMPT = "agents_prompt"
KEY_TOOLS = "tools"
KEY_TOOLS_PROMPT = "tools_prompt"
KEY_ENV_PROMPT = "env_prompt"


## Tool Calling
OPENAI_API_KEY ="OPENAI_API_KEY"


INIT_METHOD_NAME = "__init__"


### POST Agent Board REST Agent Constants
REST_POST_AGENT_ACTIVITIES = "/agent/activities"
DB_PATH_SQLLITE = "db/sqllite_database.db"
SCHEMA_SQL_PATH = "db/schema.sql"
