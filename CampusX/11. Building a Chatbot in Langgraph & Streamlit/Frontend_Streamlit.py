import streamlit as st

# with st.chat_message('user'):
#     st.text('Hi, kya haal chal bro')

# with st.chat_message('assistant'):
#     st.text("Kya baat kar raha hai bhai")

# with st.chat_message('user'):
#     st.text("Mera naam don hai")

# user_input_idhar = st.chat_input('Idhar Likhna hai')

# if user_input_idhar:
#     with st.chat_message('user'):
#         st.text(user_input_idhar)


## Bot is responding with same input message but there is no history of messages
# user_input = st.chat_input("Type Here")

# if user_input:
#     with st.chat_message('user'):
#         st.text(user_input)

#     with st.chat_message('assistant'):
#         st.text(user_input)


## With the history of message
# message_history = []

# for message in message_history:
#     with st.chat_message(message['role']):
#         st.text(message['content'])
    
# user_input = st.chat_input("Type Here")

# if user_input:

#     # First appending the messages
#     message_history.append( {"role" : "user", "content" : user_input } )
#     with st.chat_message('user'):
#         st.text(user_input)

#     # First appending the messages
#     message_history.append( {"role" : "assistant", "content" : user_input } )
#     with st.chat_message('user'):
#         st.text(user_input)

## In the previous one there was a list of messages but it get initilize everytime it is called
import streamlit as st
from chatbot_backend_langgraph import chatbot_workflow
from langchain.messages import HumanMessage

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

    response = chatbot_workflow.invoke({ "messages" : [HumanMessage(content=user_input)] }, config = CONFIG)
    ai_message = response['messages'][-1].content
    # First appending the messages
    st.session_state['message_history'].append( {"role" : "assistant", "content" : ai_message } )
    with st.chat_message('user'):
        st.text(ai_message)