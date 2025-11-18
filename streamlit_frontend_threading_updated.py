import streamlit as st
from langgraph_tool_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    # Set a temporary title until first user query
    st.session_state['thread_titles'][thread_id] = "New chat"
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        # Initialize title if not already there
        if thread_id not in st.session_state['thread_titles']:
            st.session_state['thread_titles'][thread_id] = "New chat"

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])


# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

# NEW: titles per thread_id
if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}

add_thread(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

# Show latest first
for thread_id in st.session_state['chat_threads'][::-1]:
    # Get saved title (first user query) or fallback to thread_id
    title = st.session_state['thread_titles'].get(thread_id, str(thread_id))

    # Important: give each button a unique key
    if st.sidebar.button(title, key=f"thread-btn-{thread_id}"):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages


# **************************************** Main UI ************************************

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # If this is the first message in this thread, save it as the title
    current_thread = st.session_state['thread_id']
    # Only overwrite if title is default or missing
    if (current_thread not in st.session_state['thread_titles'] or
        st.session_state['thread_titles'][current_thread] in ["New chat", str(current_thread)]):
        # Optionally truncate very long queries
        short_title = user_input.strip()
        if len(short_title) > 40:
            short_title = short_title[:37] + "..."
        st.session_state['thread_titles'][current_thread] = short_title

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # get ai response
    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
