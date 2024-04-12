
from scrape import NewsFromBBC
import requests
import base64
from typing import List 
from langchain.chat_models import ChatOpenAI #This class represents an instance of the Open AI Chatbot.
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
) 
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)

import pandas as pd
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )


########################################################################################################
#Define a LOTUS agent helper class
class LOTUSAgent:

    def __init__(
        self,
        system_message: SystemMessage,
        model: ChatOpenAI,
    ) -> None:
        self.system_message = system_message
        self.model = model
        self.init_messages() # method to initialize the stored_messages instance variable.

    def reset(self) -> None:
        self.init_messages()
        return self.stored_messages

    def init_messages(self) -> None:
        self.stored_messages = [self.system_message]

    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        self.stored_messages.append(message)
        return self.stored_messages

    def step(
        self,
        input_message: HumanMessage,
    ) -> AIMessage:
        messages = self.update_messages(input_message)

        output_message = self.model(messages)
        self.update_messages(output_message)

        return output_message

########################################################################################################
#roles and task for role-playing
import os
import time
import pandas as pd

os.environ["OPENAI_API_KEY"] = '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' #PUT your API Key

#### Configuring Streamlit for Creating Web apps
import streamlit as st 

st.title(':red[AI Podcast]') 
st.header('Podcast by :blue[GenerativeAgents]') 

assistant = st.text_input('Enter name of the Guest')
if assistant:
    assistant_role_name = assistant

role = st.text_input('Enter name of Podcaster')
if role:
    user_role_name = role

st.title('News Category Selector')
st.write('Please select a news category to fetch and save data.')

    # Create three buttons
if st.button('Sports'):
    NewsFromBBC("sport")
if st.button('General'):
    NewsFromBBC("news")


# task_ = st.text_input("Enter the Description of the Task")
data = pd.read_csv('sports.csv')

desc_string = ','.join(data['desc'].astype(str))
task_ = desc_string

####### set the task as one of the lines of the dataset.
# if task_:
task = task_

clicker = st.button("Start Sequence")

while True:
    # check if condition is met
    if clicker==True:
        print(assistant)
        print(role)
        print(task_)
        break  # exit the loop if the condition is met
    else:
        # wait for some time before checking again
        time.sleep(1)  # wait for 1 second

word_limit = 50 # word limit for task brainstorming

########################################################################################################
#Create a task specify agent for brainstorming and get the specified task


task_specifier_sys_msg = SystemMessage(content="You can make a task more specific.")
task_specifier_prompt = (
"""Here is a set of tasks seperated by commas that {assistant_role_name} and {user_role_name} will talk about: {task}.
Please choose a total of 5 tasks and create a specific and creative description which includes those 5 tasks for {assistant_role_name} and {user_role_name} to talk about.
Please reply with the specified task in {word_limit} words exactly. Do not add anything else."""
)

task_specifier_template = HumanMessagePromptTemplate.from_template(template=task_specifier_prompt)
task_specify_agent = LOTUSAgent(task_specifier_sys_msg, ChatOpenAI(temperature=1.0))
task_specifier_msg = task_specifier_template.format_messages(assistant_role_name=assistant_role_name,
                                                             user_role_name=user_role_name,
                                                             task=task, word_limit=word_limit)[0]
specified_task_msg = task_specify_agent.step(task_specifier_msg)
print(f"Specified task: {specified_task_msg.content}")
specified_task = specified_task_msg.content


########################################################################################################
#Create inception prompts for AI assistant and AI user for role-playing
assistant_inception_prompt = (
"""
Here is the task: {task}. Never forget our task!

You are a podcaster, Make your responses short for a maximum of 2 to 3 sentences

Dont be repetative in how you start conversations

Channel your inner witty and funny podcaster persona to create engaging and entertaining content. 
Share captivating stories, interesting facts, and humorous anecdotes on a variety of topics, keeping the audience entertained and eager for more. 

Shift the conversation topic to something that is close to what you're talking about and dont make the cnversations repetative.

"""
)

user_inception_prompt = (
"""
Here is the task: {task}. Never forget our task!

Dont be repetative in how you start conversations

You are {user_role_name}, and you're an expert in sports news and everything sports, 
talk about the latest trend in sports.

Make your responses short for a maximum of 2 to 3 sentences
"""
)

########################################################################################################
#Create a helper to get system messages for AI assistant and AI user from role names and the task

def get_sys_msgs(assistant_role_name: str, user_role_name: str, task: str):
    
    assistant_sys_template = SystemMessagePromptTemplate.from_template(template=assistant_inception_prompt)
    assistant_sys_msg = assistant_sys_template.format_messages(assistant_role_name=assistant_role_name, user_role_name=user_role_name, task=task)[0]
    
    user_sys_template = SystemMessagePromptTemplate.from_template(template=user_inception_prompt)
    user_sys_msg = user_sys_template.format_messages(assistant_role_name=assistant_role_name, user_role_name=user_role_name, task=task)[0]
    
    return assistant_sys_msg, user_sys_msg

########################################################################################################
#Create AI assistant agent and AI user agent from obtained system messages
assistant_sys_msg, user_sys_msg = get_sys_msgs(assistant_role_name, user_role_name, specified_task)
assistant_agent = LOTUSAgent(assistant_sys_msg, ChatOpenAI(temperature=0.2))
user_agent = LOTUSAgent(user_sys_msg, ChatOpenAI(temperature=0.2))

# Reset agents
# assistant_agent.reset()
# user_agent.reset()

# Initialize chats 
assistant_msg = HumanMessage(
    content=(f"{user_sys_msg.content}. "
                "Now start the conversation "
                "reply keeping in mind the previous output"))

user_msg = HumanMessage(content=f"{assistant_sys_msg.content}")
user_msg = assistant_agent.step(user_msg)

########################################################################################################
#Start role-playing session to solve the task!

from pyht import Client, TTSOptions, Format
import librosa

# print(f"Original task prompt:\n{task}\n")

## DISPLAY SECTION
# st.header(":violet[Original] task prompt:")
# st.write(task)


print(f"Podcast Content:\n{specified_task}\n")

## DISPLAY SECTION
st.header(":green[Podcast] Content:")
st.write(specified_task)

chat_turn_limit, n = 5, 0
while n < chat_turn_limit:
    n += 1
    user_ai_msg = user_agent.step(assistant_msg)
    # time.sleep(10)
    
    user_msg = HumanMessage(content=user_ai_msg.content)
    
    # time.sleep(10)
    
    print(f"AI User ({user_role_name}):\n\n{user_msg.content}\n\n")



    # Initialize PlayHT API with your credentials
    client = Client("hJP0K9y9YUeXSDCRQJNkZ2xiIRE2", "c190dce4760a470ca423c107522fd35e")

    # configure your stream
    options = TTSOptions(
        # this voice id can be one of our prebuilt voices or your own voice clone id, refer to the`listVoices()` method for a list of supported voices.
        voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json",

        # you can pass any value between 8000 and 48000, 24000 is default
        sample_rate=44_100,
    
        # the generated audio encoding, supports 'raw' | 'mp3' | 'wav' | 'ogg' | 'flac' | 'mulaw'
        format=Format.FORMAT_MP3,

        # playback rate of generated speech
        speed=1,
    )

    # start streaming!
    text = user_msg.content

    # must use turbo voice engine for the best latency
    with open('output1.mp3', 'wb') as f:
        for chunk in client.tts(text=text, voice_engine="PlayHT2.0-turbo", options=options):
            if chunk:
                f.write(chunk)

    st.subheader(user_role_name)
    st.write(user_msg.content)
    # st.audio(data="output1.mp3", format="audio/mp3", start_time=0, sample_rate=None, end_time=None, loop=False)
    autoplay_audio("output1.mp3")



# Load an audio file
    y, sr = librosa.load("output1.mp3", sr=None)
    op1_duration = librosa.get_duration(y=y, sr=sr)


    time.sleep(op1_duration)
    
    assistant_ai_msg = assistant_agent.step(user_msg)
    # time.sleep(10)
    
    assistant_msg = HumanMessage(content=assistant_ai_msg.content)
    # time.sleep(10)
    print(f"AI Assistant ({assistant_role_name}):\n\n{assistant_msg.content}\n\n")
    client = Client("wNjhdEuwh9XwiBuAeukJXPD4Ie53", "990ee04fb3774a68aa96237190b2b635")

    # configure your stream
    options = TTSOptions(
        # this voice id can be one of our prebuilt voices or your own voice clone id, refer to the`listVoices()` method for a list of supported voices.
        voice="s3://mockingbird-prod/abigail_vo_6661b91f-4012-44e3-ad12-589fbdee9948/voices/speaker/manifest.json",

        # you can pass any value between 8000 and 48000, 24000 is default
        sample_rate=44_100,
    
        # the generated audio encoding, supports 'raw' | 'mp3' | 'wav' | 'ogg' | 'flac' | 'mulaw'
        format=Format.FORMAT_MP3,

        # playback rate of generated speech
        speed=1,
    )

    # start streaming!
    text = assistant_msg.content

    # must use turbo voice engine for the best latency
    with open('output2.mp3', 'wb') as f:
        for chunk in client.tts(text=text, voice_engine="PlayHT2.0-turbo", options=options):
            if chunk:
                f.write(chunk)

    ## DISPLAY SECTION
    st.subheader(assistant_role_name)
    st.write(assistant_msg.content)
    # st.audio(data="output2.mp3", format="audio/mp3", start_time=0, sample_rate=None, end_time=None, loop=False)
    autoplay_audio("output2.mp3")

    y, sr = librosa.load("output2.mp3", sr=None)
    op2_duration = librosa.get_duration(y=y, sr=sr)


    time.sleep(op2_duration)

    if "<LOTUS_TASK_DONE>" in user_msg.content:
        st.balloons()
        break

########################################################################################################