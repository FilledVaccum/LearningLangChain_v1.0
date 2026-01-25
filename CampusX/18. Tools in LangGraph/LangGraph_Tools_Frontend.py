import streamlit as st
from LangGraph_Tools_Backend import chatbot_workflow, retrive_All_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ********************************** Utility Function **********************************

# We need to create the thread it for every new chat
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

# We also need to store thread somewhere to retrieve it
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

# We also need to have an option to reset chat - fresh chat
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

# We need to load conversation
def load_conversation(thread_id):
    state = chatbot_workflow.get_state(config = { 'configurable' : { 'thread_id' : thread_id } })
    # Check if they key exists in state values , return empty list if not
    return state.values.get('messages', [])

# ********************************** Session Setup **********************************

# Initialize message history
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Initialize thread ID (current conversation)
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# Initialize list of all threads - Since you are storing the thread in db - you need to load it
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrive_All_threads()

# Register current thread
add_thread(st.session_state['thread_id'])

# ********************************** Sidebar UI **********************************
# This UI element would be on sidebar 
st.sidebar.title('LangGraph Chatbot')

# Button for new chat and it will create new thread
if st.sidebar.button('New Chat'):
    reset_chat()

## Conversation List Header
st.sidebar.header("My Conversations")

# - Section header for listing all past conversations
## Display All Conversations
for thread_id in st.session_state['chat_threads'][::-1]:
    
    ### Load Conversation on Click
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        ### Convert Messages to Display Format
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

if user_input:

    # First add the message to message history 
    st.session_state['message_history'].append( { 'role' : 'user', 'content' : user_input } )
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = { 
        'configurable' : { 'thread_id' : st.session_state['thread_id']},
        'metadata': {
            'thread_id' : st.session_state['thread_id'],
            },
        'run_name' : 'Chat_Turn'
        }

    # Stream with tool status display
    status_container = st.status("Processing...", expanded=False)
    
    tool_used = False
    for message_chunk, metadata in chatbot_workflow.stream(
        { 'messages' : [HumanMessage(content = user_input)]}, 
        config = CONFIG,
        stream_mode = 'messages'
    ):
        # Show tool calls in status
        if isinstance(message_chunk, AIMessage) and hasattr(message_chunk, 'tool_calls') and message_chunk.tool_calls:
            tool_used = True
            for tool_call in message_chunk.tool_calls:
                status_container.write(f"🔧 Using: {tool_call['name']}")
    
    status_container.update(label="Complete", state="complete")
    
    # Get final response
    state = chatbot_workflow.get_state(config = CONFIG)
    final_message = state.values['messages'][-1]
    
    with st.chat_message("assistant"):
        st.text(final_message.content)
    
    ai_message = final_message.content

    ## 6. Save AI Response
    st.session_state['message_history'].append( { 'role' : 'assistant', 'content' : ai_message } )