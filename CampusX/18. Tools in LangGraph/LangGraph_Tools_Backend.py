from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, BaseMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import sqlite3
from rich import print as rprint

# New Imports
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from ddgs import DDGS
import requests
import os

# Loading Environment Variable
load_dotenv()

# Create an instance using init_chat_model class
llm = init_chat_model('gpt-5-nano')

# ---------------- Tools --------------------
# Search Tool
@tool
def search_tool(query: str) -> str:
    """Search the web using DuckDuckGo for the given query."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
        return str(results)

@tool
def calculator(first_num : float, second_num : float, operation: str) -> dict:
    """
    Perform basic arithmetic operation on two numbers.
    Supported Operations: add, sub, mul, div
    """

    try:
        if operation == 'add':
            result = first_num + second_num
        elif operation == 'sub':
            result = first_num - second_num
        elif operation == 'mul':
            result = first_num * second_num
        elif operation == 'div':
            if second_num == 0:
                return { 'error' : "Division by Zero is not Allowed" }
            else:
                result = first_num / second_num
        else:
            return { 'error' : f"Unsupported Operation '{operation}'" }

        return { 'first_num' : first_num, "second_num" : second_num, 'operation' : operation, "result": result}
    except Exception as e:
        return { 'error': str(e) }

@tool
def get_stock_price(symbol : str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g 'AAPL', 'TSLA')
    Using Alpha Vantage with API key in the URL.
    """
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    return r.json()


# Putting Tools in a list 
tools = [search_tool, get_stock_price, calculator]
llm_with_tools = llm.bind_tools(tools)

# Create a state for the graph which has a single key 'messages'
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

# Creating a node - that store retrieve message from state -> Send it to the model -> Get the response and return that message key to get save
def chat_node(state: ChatState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return { 'messages' : response }

# Tool Node
tool_node = ToolNode(tools)

# Creating an SQlite Connection
conn = sqlite3.connect(database='chatbot.db', check_same_thread = False) # Setting it false we are going to use this db in multiple conv - threads 

# Checkpointer to make sure to store the data in sqlite
checkpointer = SqliteSaver(conn=conn)

# Creating the graph, adding Nodes and Edges
chatbot_graph = StateGraph(ChatState)

chatbot_graph.add_node('chat_node', chat_node)
chatbot_graph.add_node('tools', tool_node)

chatbot_graph.add_edge(START, 'chat_node')
chatbot_graph.add_conditional_edges('chat_node', tools_condition)

chatbot_graph.add_edge('chat_node', END)

# Compiling the graph
chatbot_workflow = chatbot_graph.compile(checkpointer = checkpointer)

# ------- Helper Function -------------
def retrive_All_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    
    return list(all_threads)