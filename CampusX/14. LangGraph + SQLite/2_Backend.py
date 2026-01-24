from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, BaseMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import sqlite3
from rich import print as rprint

# Loading Environment Variable
load_dotenv()

# Create an instance using init_chat_model class
model = init_chat_model('gpt-5-nano')

# Create a state for the graph which has a single key 'messages'
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

# Creating a node - that store retrieve message from state -> Send it to the model -> Get the response and return that message key to get save
def chat_node(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return { 'messages' : response }

# Creating an SQlite Connection
conn = sqlite3.connect(database='chatbot.db', check_same_thread = False) # Setting it false we are going to use this db in multiple conv - threads 

# Checkpointer to make sure to store the data in sqlite
checkpointer = SqliteSaver(conn=conn)

# Creating the graph, adding Nodes and Edges
chatbot_graph = StateGraph(ChatState)
chatbot_graph.add_node('chat_node', chat_node)
chatbot_graph.add_edge(START, 'chat_node')
chatbot_graph.add_edge('chat_node', END)

# Compiling the graph
chatbot_workflow = chatbot_graph.compile(checkpointer = checkpointer)

CONFIG = { 'configurable' : { 'thread_id' : 'thread_1' } }

response = chatbot_workflow.invoke(
    { 'messages' : [HumanMessage(content= "Create a song on my name.")]},
    config = CONFIG
)

rprint(response)

# def retrieve_all_threads():
#     all_threads = set()
#     for checkpoint in checkpointer.list(None):
#         all_threads.add(checkpoint.config['configurable']['thread_id'])

#     return list(all_threads)