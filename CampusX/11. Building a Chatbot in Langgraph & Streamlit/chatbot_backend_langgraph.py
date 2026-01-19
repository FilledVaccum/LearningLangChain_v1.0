from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain.chat_models import init_chat_model
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

# Initilizing the model
model = init_chat_model("gpt-5-nano")

# Defining the Class - that represent the state
class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

# Defining the Node - will be used in graph
def chat_node(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return { "messages" : [response] }

# Checkpointer
checkpointer = InMemorySaver()

# Defining the Graph
chatbot_graph = StateGraph(ChatState)
chatbot_graph.add_node('chat_node', chat_node)
chatbot_graph.add_edge(START, 'chat_node')
chatbot_graph.add_edge('chat_node', END)

# Compile the graph
chatbot_workflow = chatbot_graph.compile(checkpointer = checkpointer)