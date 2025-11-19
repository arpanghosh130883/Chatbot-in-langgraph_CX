import streamlit as st
from langgraph_tool_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    return uuid.uuid4()

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])


# **************************************** Session Setup ******************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    # No active thread until first message is sent
    st.session_state['thread_id'] = None

if 'chat_threads' not in st.session_state:
    # List of thread_ids that already have at least one message
    st.session_state['chat_threads'] = []

if 'thread_titles' not in st.session_state:
    # Mapping: thread_id -> title (first user query)
    st.session_state['thread_titles'] = {}

if 'pending_new_chat' not in st.session_state:
    # True means we're waiting for the first message of a new conversation
    st.session_state['pending_new_chat'] = True


# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

# New Chat button: just clear the current view and mark that the next message
# starts a brand-new conversation. We DO NOT create a thread yet.
if st.sidebar.button('New Chat'):
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = None
    st.session_state['pending_new_chat'] = True

st.sidebar.header('My Conversations')

# Show latest first
for thread_id in st.session_state['chat_threads'][::-1]:
    # Get saved title or fallback to thread_id string
    title = st.session_state['thread_titles'].get(thread_id, str(thread_id))

    # Important: give each button a unique key
    if st.sidebar.button(title, key=f"thread-btn-{thread_id}"):
        st.session_state['thread_id'] = thread_id
        st.session_state['pending_new_chat'] = False  # we're in an existing chat
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

# Display the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # If this is the first message of a brand new chat, create a new thread now.
    if st.session_state.get('pending_new_chat', False) or st.session_state.get('thread_id') is None:
        new_thread_id = generate_thread_id()
        st.session_state['thread_id'] = new_thread_id
        st.session_state['pending_new_chat'] = False

        # Add to the list of conversations
        if new_thread_id not in st.session_state['chat_threads']:
            st.session_state['chat_threads'].append(new_thread_id)

        # Use the first user message as the title (truncated)
        short_title = user_input.strip()
        if len(short_title) > 40:
            short_title = short_title[:37] + "..."
        st.session_state['thread_titles'][new_thread_id] = short_title

    else:
        # Existing thread: don't change the title here
        pass

    current_thread = st.session_state['thread_id']

    # First add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': current_thread}}

    # Get AI response
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
