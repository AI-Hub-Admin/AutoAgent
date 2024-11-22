# AutoAgent: Awesome Autonomous Agents Repo and Asynchronous Environment for public available Autonomous Agents

This is the official github repo of pypi package AutoAgent (https://pypi.org/project/AutoAgent). This repo is intended to provide common interface of Autonomous Agents async runing, debuging, deployment.
To contribute the AutoAgent repo, you can visit the guidelines at (http://www.deepnlp.org/blog?category=agent)

Autonomous Agents is becoming more popular than ever and can help enterprise reduce costs and boost revenue, such as [https://blogs.microsoft.com/blog/2024/10/21/new-autonomous-agents-scale-your-team-like-never-before/](https://blogs.microsoft.com/blog/2024/10/21/new-autonomous-agents-scale-your-team-like-never-before/) and Claude's Computer Use Autonommous AI Agents(https://docs.anthropic.com/en/docs/build-with-claude/computer-use).


## Awesome AI Agents Resources and Public Reviews

|  Project  | Agent Sub-Category | Developer| URL | AI Agent Reviews  |
|  ----  | ----  | ----  | ----  | ----  | 
|  AutoGen  | AI Agent Framework  | Microsoft  | https://microsoft.github.io/autogen/0.2/  | http://www.deepnlp.org/store/pub/pub-microsoft-ai-agent  | 
|  AgentGPT  | AI Agent Framework  | Reworkd  | https://github.com/reworkd/AgentGPT  | http://www.deepnlp.org/store/pub/pub-agentgpt | 
|  Claude Computer Use Agent | Automomous Agent  | Anthropic |  https://docs.anthropic.com/en/docs/build-with-claude/computer-use | http://www.deepnlp.org/store/pub/pub-microsoft-ai-agent  | 
|  OpenAI AI Agent 'Operator' | Automomous Agent  | OpenAI |  TBD | http://www.deepnlp.org/store/pub/pub-openai-ai-agent  | 
|  AgentForce | AI Agent Application | Saleforce |  https://www.salesforce.com/agentforce/ | http://www.deepnlp.org/store/pub/pub-salesforce-ai-agent  | 
|  AutoGLM | AutoGLM Phone Use | Zhipu AI | https://xiao9905.github.io/AutoGLM | http://www.deepnlp.org/store/pub/pub-zhipu-ai |


## AutoAgent and AgentBoard Packages

To help visualize the development and running process of AI Agents, we provide "AutoAgent" and "agentboard". 

**AutoAgent** is a common async run loop wrapper of AI agents, compatible with most of the LLM APIs and local models. 

**AgentBoard** is a project (https://github.com/AI-Hub-Admin/agentboard), just like "tensorboard" to visualize tensors of model training, help visualize the detailed process, workflow, text, audio, image input and output of Agent running with cutomized loging functions. For the tutorial of agentboard, you can visit ([AgentBoard: AI Agent Visualization Toolkit for Agent Loop Workflow RAG Tool Use Functions Callings and Multi Modal Data Visualization](http://www.deepnlp.org/blog/agentBoard-ai-agent-visualization-toolkit-agent-loop-workflow))


You can first setup the agentboard and start a web admin page as in the repo (https://github.com/AI-Hub-Admin/agentboard). 
It comes with a default minimal functioning Community GUI (X/twitter style) to visualze difference phases (plan/act/react/reflect) of Autonomous AI Agent Loop.


**Auto Plan AI Agents** <br>
![Auto Plan Agent](https://github.com/AI-Hub-Admin/AutoAgent/blob/main/docs/auto_plan_agent_1.jpg?raw=true)


**Website Admin AI Agents** <br>
![WebAdmin Automatic Comment Agent](https://github.com/AI-Hub-Admin/AutoAgent/blob/main/docs/auto_comment_agent_2.jpg?raw=true)



## Install
```
pip install AutoAgent agentboard
```

### Setup agentboard for Visualization

Cloning From Github

```
git clone https://github.com/AI-Hub-Admin/agentboard.git

# rm old sqllite db file
cd /src/
rm sqllite_database.db 

## init the db
python3 db_sqllite.py

## run the webpage server
python3 run_agent_board.py

```

Using Command Line


```
## cmd line
agentboard

# agentboard --logdir=./log --static=./static --port=5000 
```

You can visit URL: http://127.0.0.1:5000/agent to see if the agentboard run successfully. 



## AutoAgent QuickStart

### Example 1 AutoPlan Agent

Task: Initialize two AI Agents to plan today's activities and post on the X (web simulator). 

**agent 1**: Tom is a young boy <br>
**agent 2**: Tom's dad <br>

In the plan->act->reflect agent loop. 

**PLAN**: Agent will make plans for their days and split the plans output into separate actions. <br>
**ACT**: Take Actions, and post their planned activities on the agentboard X webpage.  <br>
**REFLECT**: At the end of the day, make a summary of their day. <br>


![Autonomous Plan Agent](https://github.com/AI-Hub-Admin/AutoAgent/blob/main/docs/auto_comment_agent_1.jpg?raw=true)


Full implementation in folder /examples/auto_plan_agent/run_agents_plan_a_day.py

```


    agent1_prompt = """You are playing the role of Tom a 5 year old boy. Your Task is to make plans for today, and you can choose activities from 'go to school, play with Jack, swimming', you can decide what how long"
     At the end of the day, you need to make a summary of your daily activities and make a selfie and posted on the website"""
    agent2_prompt = """You are playing the role of Tom's dad and you are making plans for today, you can choose between having breakfast, go to company, 
    have meetings with clients. But at 5:00 pm, you have to pick up tom, your son from school.  At the end of the day, you should take a picture with your boy Tom and send to his mother, Lily."""

    agent1 = AutoPlanAgent(name="Tom", instructions=agent1_prompt, avatar="icon_children.jpg", debug=True)
    agent2 = AutoPlanAgent(name="Daddy", instructions=agent2_prompt, avatar="icon_male.jpg", debug=True)

    agents = [agent1, agent2]
    # agents = [AutoPlanAgent(name=agent_name, instructions=prompt, avatar=avatar, debug=True) for i, (agent_name, prompt, avatar) in enumerate(zip(agents_name, prompt_list, agents_avatar))]
    env = AsyncAutoEnv(get_openai_client(), agents=agents)
    results = env.run()


```

You can visit your webpage at: http://127.0.0.1:5000/agent and see two agents, Tom and Dad posting on your timeline in a asynchronous order as in the snapshot.



### Example 2: Web Administration Agent

The use case covers a typical scene of Website Administrator AI Agents. 

![WebAdmin Auto Comment AI Agent](https://github.com/AI-Hub-Admin/AutoAgent/blob/main/docs/auto_comment_agent_2.jpg?raw=true)



**agent 1**: Website Comment Content Auditor

Task: Audit the content that user publish on the website to see if it's spam, if it's spam, change the status to 0 (offline). Otherwise, change the status to 1 (online). There is decision process in the task.


**PLAN** : In a while loop, check if the trigger status is true, such as there are newly published pending contents.
**ACT**: Call Tools to decide if it's spam and post RESTFUL URL to the agentboard
**REFLECT**: NA


**agent 2**: Website Automatic Comment Agent 

Task: Whenever there are new contents published by users and status is online for display, give some welcome comment to the post and increase the engagement of users. 


**PLAN** : In a while loop, check if the trigger status is true, such as there are new posts published with no comments still. 
**ACT**: Take Actions, Call Tools to generate reply, and post a replies to the newly published posts.
**REFLECT**: NA



Full implementation in folder /examples/web_admin_agent/run_agents_webadmin.py


```


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

```


## Agents Related Pipeline Workflow and Document
### Related Blogs <br>
[AgentBoard Workflow](http://www.deepnlp.org/blog/agentBoard-ai-agent-visualization-toolkit-agent-loop-workflow) <br>
[AgentBoard Documents](https://ai-hub-admin.github.io/agentboard) <br>
[AutoAgent Documents](https://ai-hub-admin.github.io/AutoAgent) <br>
[DeepNLP AI Agents Designing Guidelines](http://www.deepnlp.org/blog?category=agent) <br>
[Introduction to multimodal generative models](http://www.deepnlp.org/blog/introduction-to-multimodal-generative-models) <br>
[Generative AI Search Engine Optimization](http://www.deepnlp.org/blog/generative-ai-search-engine-optimization-how-to-improve-your-content) <br>
[AI Image Generator User Reviews](http://www.deepnlp.org/store/image-generator) <br>
[AI Video Generator User Reviews](http://www.deepnlp.org/store/video-generator) <br>
[AI Chatbot & Assistant Reviews](http://www.deepnlp.org/store/chatbot-assistant) <br>
[Best AI Tools User Reviews](http://www.deepnlp.org/store/pub/) <br>
[AI Boyfriend User Reviews](http://www.deepnlp.org/store/chatbot-assistant/ai-boyfriend) <br>
[AI Girlfriend User Reviews](http://www.deepnlp.org/store/chatbot-assistant/ai-girlfriend) <br>


### AI Services Reviews and Ratings <br>
##### AI Agent
[Microsoft AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-microsoft-ai-agent) <br>
[Claude AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-claude-ai-agent) <br>
[OpenAI AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-openai-ai-agent) <br>
[AgentGPT AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-agentgpt) <br>
[Saleforce AI Agents Reviews](http://www.deepnlp.org/store/pub/pub-salesforce-ai-agent) <br>
##### Chatbot
[OpenAI o1 Reviews](http://www.deepnlp.org/store/pub/pub-openai-o1) <br>
[ChatGPT User Reviews](http://www.deepnlp.org/store/pub/pub-chatgpt-openai) <br>
[Gemini User Reviews](http://www.deepnlp.org/store/pub/pub-gemini-google) <br>
[Perplexity User Reviews](http://www.deepnlp.org/store/pub/pub-perplexity) <br>
[Claude User Reviews](http://www.deepnlp.org/store/pub/pub-claude-anthropic) <br>
[Qwen AI Reviews](http://www.deepnlp.org/store/pub/pub-qwen-alibaba) <br>
[Doubao Reviews](http://www.deepnlp.org/store/pub/pub-doubao-douyin) <br>
[ChatGPT Strawberry](http://www.deepnlp.org/store/pub/pub-chatgpt-strawberry) <br>
[Zhipu AI Reviews](http://www.deepnlp.org/store/pub/pub-zhipu-ai) <br>
##### AI Image Generation
[Midjourney User Reviews](http://www.deepnlp.org/store/pub/pub-midjourney) <br>
[Stable Diffusion User Reviews](http://www.deepnlp.org/store/pub/pub-stable-diffusion) <br>
[Runway User Reviews](http://www.deepnlp.org/store/pub/pub-runway) <br>
[GPT-5 Forecast](http://www.deepnlp.org/store/pub/pub-gpt-5) <br>
[Flux AI Reviews](http://www.deepnlp.org/store/pub/pub-flux-1-black-forest-lab) <br>
[Canva User Reviews](http://www.deepnlp.org/store/pub/pub-canva) <br>
##### AI Video Generation
[Luma AI](http://www.deepnlp.org/store/pub/pub-luma-ai) <br>
[Pika AI Reviews](http://www.deepnlp.org/store/pub/pub-pika) <br>
[Runway AI Reviews](http://www.deepnlp.org/store/pub/pub-runway) <br>
[Kling AI Reviews](http://www.deepnlp.org/store/pub/pub-kling-kwai) <br>
[Dreamina AI Reviews](http://www.deepnlp.org/store/pub/pub-dreamina-douyin) <br>
##### AI Education
[Coursera Reviews](http://www.deepnlp.org/store/pub/pub-coursera) <br>
[Udacity Reviews](http://www.deepnlp.org/store/pub/pub-udacity) <br>
[Grammarly Reviews](http://www.deepnlp.org/store/pub/pub-grammarly) <br>
##### Robotics
[Tesla Cybercab Robotaxi](http://www.deepnlp.org/store/pub/pub-tesla-cybercab) <br>
[Tesla Optimus](http://www.deepnlp.org/store/pub/pub-tesla-optimus) <br>
[Figure AI](http://www.deepnlp.org/store/pub/pub-figure-ai) <br>
[Unitree Robotics Reviews](http://www.deepnlp.org/store/pub/pub-unitree-robotics) <br>
[Waymo User Reviews](http://www.deepnlp.org/store/pub/pub-waymo-google) <br>
[ANYbotics Reviews](http://www.deepnlp.org/store/pub/pub-anybotics) <br>
[Boston Dynamics](http://www.deepnlp.org/store/pub/pub-boston-dynamic) <br>
##### AI Tools
[DeepNLP AI Tools](http://www.deepnlp.org/store/pub/pub-deepnlp-ai) <br>
##### AI Widgets
[Apple Glasses](http://www.deepnlp.org/store/pub/pub-apple-glasses) <br>
[Meta Glasses](http://www.deepnlp.org/store/pub/pub-meta-glasses) <br>
[Apple AR VR Headset](http://www.deepnlp.org/store/pub/pub-apple-ar-vr-headset) <br>
[Google Glass](http://www.deepnlp.org/store/pub/pub-google-glass) <br>
[Meta VR Headset](http://www.deepnlp.org/store/pub/pub-meta-vr-headset) <br>
[Google AR VR Headsets](http://www.deepnlp.org/store/pub/pub-google-ar-vr-headset) <br>
##### Social
[Character AI](http://www.deepnlp.org/store/pub/pub-character-ai) <br>
##### Self-Driving
[BYD Seal](http://www.deepnlp.org/store/pub/pub-byd-seal) <br>
[Tesla Model 3](http://www.deepnlp.org/store/pub/pub-tesla-model-3) <br>
[BMW i4](http://www.deepnlp.org/store/pub/pub-bmw-i4) <br>
[Baidu Apollo Reviews](http://www.deepnlp.org/store/pub/pub-baidu-apollo) <br>
[Hyundai IONIQ 6](http://www.deepnlp.org/store/pub/pub-hyundai-ioniq-6) <br>
