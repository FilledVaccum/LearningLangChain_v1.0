import streamlit as st
from Backend_Langgraph import chatbot_workflow
from langchain_core.messages import HumanMessage

CONFIG = {
    "configurable" : { "thread_id" : "thread-1" }
}

# st.session_state -> dict ->
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
    
user_input = st.chat_input("Type Here")

if user_input:

    # First appending the messages
    st.session_state['message_history'].append( {"role" : "user", "content" : user_input } )
    with st.chat_message('user'):
        st.text(user_input)

    # First appending the messages
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot_workflow.stream(
                { "messages" : [HumanMessage(content=user_input)]}, 
                config = CONFIG,
                stream_mode = 'messages'
            )
            if message_chunk.content  # ← Filter empty chunks
        )

    st.session_state['message_history'].append( {"role" : "assistant", 'content' : ai_message} )