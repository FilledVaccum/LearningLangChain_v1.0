from streamlit as st
from Backend_Langgraph import chatbot_workflow
from langchain_core.message import HumanMessage, AIMessage
import uuid


# ********************************** Utility Function **********************************
# We need to create the thread ID for every new chat
def generate_thread_id():
    thread_id = uuid.uuid()
    return thread_id

# We also need to store the thread somewhere to retrieve it
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

# We also need to have an option to reset chat - start a fresh chat
def reset_chat():
    thread_id = generate_thread_id()
    st.sesion_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

# We need to load the conversation
def load_conversation(thread_id):
    CONFIG = { 'configurable' : { 'thread_id' : thread_id }}
    state = chatbot_workflow.get_state(config = CONFIG) 
    # Check if the key exists in state values, return empty list if not
    return state.values.get('messages', [])


# ********************************** Session Setup **********************************
# Initialize message history
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Initilize thread ID (Current Conversation)
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# Initialize list of all threads
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

# Register Current Thread
add_threads(st.session_state['thread_id'])

# ********************************** Sidebar UI **********************************
# This UI element would be on sidebar
st.sidebar.title('LangGraph Chatbot')

# Button for new chat and it will create new thread
if st.sidebat.button('New Chat'):
    reset_chat()

# Conversation List Header
st.sidebar.header('My Conversation')

# Section header for listing all past conversations
## Display All Conversation
for thread_id in st.session_state['chat_threads'][::-1]:

    # Load Conversation on Click
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        # Convert Messafes to Display Format
        temp_message = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_message.append( { 'role' : role, 'content' : msg.content } )

        st.session_state['message_history'] = temp_message

# ********************************** Main UI **********************************
# Loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type Here')

# Handle New User Message
if user_input:
    # First add the message to message history
    st.session_state['message_history'].append( { 'role' : 'user', 'content' : user_input } )

    with st.chat_message('user'):
        st.text(user_input)
        
    # Configure Thread
    CONFIG = { 'configurable' : { 'thread_id' : st.session_state['thread_id'] } }

    # Stream AI Response
    with st.chat_message('assistant'):
        def ai_only_stream():
            for message_chunk, metadata in chatbot_workflow.stream(
                { 'message' : [HumanMessage(content = user_input)] },
                config = CONFIG,
                stream_mode = 'messages'
            ):
                if isinstance(message_chunk, AIMessage):
                    # Yield only Assistant Tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    # Save AI Response
    st.session_state['message_history'].append( {'role' : 'assistant' , 'content' : ai_message } )