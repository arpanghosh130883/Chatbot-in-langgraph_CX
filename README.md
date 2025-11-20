###############################  How we are replacing the ThreadID with Chat first query  ##################################

1️⃣ When you type the first message of a chat

This block is the key:

user_input = st.chat_input('Type here')

# If user sends a message that should start a new conversation:
if user_input and (st.session_state['pending_new_chat'] or st.session_state['thread_id'] is None):
    new_thread_id = generate_thread_id()
    st.session_state['thread_id'] = new_thread_id
    st.session_state['pending_new_chat'] = False

    # Add to list of conversations (will appear immediately in sidebar)
    if new_thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(new_thread_id)

    # Use first user query as title (truncate if long)
    short_title = user_input.strip()
    if len(short_title) > 40:
        short_title = short_title[:37] + "..."
    st.session_state['thread_titles'][new_thread_id] = short_title


What happens here?

user_input gets your text, e.g. "Explain the transformer architecture".

If this is a new chat (pending_new_chat is True or thread_id is None):

A new thread_id (UUID) is created.

That thread_id is added to chat_threads.

Then we compute short_title from user_input:

short_title = "Explain the transformer architecture" (possibly truncated).

We store this in:

st.session_state['thread_titles'][new_thread_id] = short_title


So now we have a mapping like:

thread_titles = {
    <some-uuid>: "Explain the transformer architecture ..."
}


That’s where the “first query name” is captured.

2️⃣ How the sidebar shows the title instead of the UUID

Later, in the sidebar loop:

st.sidebar.header('My Conversations')

# Show latest conversations first
for thread_id in st.session_state['chat_threads'][::-1]:
    title = st.session_state['thread_titles'].get(thread_id, str(thread_id))

    if st.sidebar.button(title, key=f"thread-btn-{thread_id}"):
        ...


For each thread_id:

We look up its title:

title = st.session_state['thread_titles'].get(thread_id, str(thread_id))


If we have stored a title, title becomes that first query text.

Only if nothing is stored do we fall back to str(thread_id) (the UUID).

We pass title to the button:

st.sidebar.button(title, key=f"thread-btn-{thread_id}")


So the button label is “Explain the transformer architecture …”, not the UUID.

3️⃣ Put very simply

Capture first query → store as title:

st.session_state['thread_titles'][new_thread_id] = user_input_short


Read that title for display:

title = st.session_state['thread_titles'].get(thread_id, str(thread_id))
st.sidebar.button(title, ...)


#######################################################################################################################

########################################### How user first query as we type immediately gets added on the sidebar  after clsicking on New Chat  ##########################

Changes Made (Bullet-Point Summary)
1. Thread Creation Logic

❌ Original: A new thread was created immediately when clicking New Chat.

✅ Updated: A new thread is created only when the first user query is typed, not when clicking New Chat.


Before
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)

After
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None  # No thread until first message

if 'pending_new_chat' not in st.session_state:
    st.session_state['pending_new_chat'] = True

    

2. No More “New chat” Dummy Thread

❌ Original: Every new session created a placeholder thread with a UUID before any message.

❌ This resulted in “New chat” appearing in My Conversations.

✅ Updated: The app starts with no thread.

➜ A conversation appears only after the user sends the first message.



Before
add_thread(st.session_state['thread_id'])  # Adds empty thread immediately

After

###### Thread is created only when user types first message
if user_input and (st.session_state['pending_new_chat'] or st.session_state['thread_id'] is None):
    new_thread_id = generate_thread_id()
    st.session_state['thread_id'] = new_thread_id



3. Thread Title Instead of Thread ID

❌ Original: Sidebar buttons showed the thread_id (UUID string).

✅ Updated: Sidebar buttons show the first user query, truncated to 40 characters.


Before
for thread_id in st.session_state['chat_threads'][::-1]:
    st.sidebar.button(str(thread_id))

After
title = st.session_state['thread_titles'].get(thread_id, str(thread_id))
st.sidebar.button(title, key=f"thread-btn-{thread_id}")



4. First Query Renames Chat Immediately (Fixed Sidebar Timing)

❌ Original: Title updated after rerun, so rename appeared only after clicking New Chat.

✅ Updated: Thread is created before the sidebar is rendered, so sidebar updates immediately.



Before

(Sidebar renders before thread is created → no title update)

user_input = st.chat_input('Type here')
# Title not updated until after sidebar reruns

After

(Thread creation happens BEFORE sidebar rendering)

user_input = st.chat_input('Type here')

if user_input and (st.session_state['pending_new_chat'] or st.session_state['thread_id'] is None):
    new_thread_id = generate_thread_id()
    st.session_state['thread_id'] = new_thread_id

    short_title = user_input.strip()[:40]
    st.session_state['thread_titles'][new_thread_id] = short_title


    

5. Added pending_new_chat Flag

❌ Not present in original.

✅ Added to determine if the next input should start a brand-new conversation.



Before
# No concept of pending new chat

After
if 'pending_new_chat' not in st.session_state:
    st.session_state['pending_new_chat'] = True


Used here:

if st.sidebar.button('New Chat'):
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = None
    st.session_state['pending_new_chat'] = True
    

6. Removed reset_chat() and add_thread() Dependency

❌ Original had:

reset_chat()

add_thread()

These auto-created threads without messages.

✅ Updated code completely removed reset_chat() logic.

➜ Instead, new threads are created dynamically on first message.



Before
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

After

Both functions removed — replaced with logic inside input handler:

if user_input and (st.session_state['pending_new_chat'] or st.session_state['thread_id'] is None):
    new_thread_id = generate_thread_id()
    st.session_state['thread_id'] = new_thread_id
    st.session_state['chat_threads'].append(new_thread_id)

    

7. Sidebar “New Chat” Button Behaviour Changed

❌ Original: Clicking “New Chat” immediately created a new thread.

❌ Auto-added to chat list even if the user didn’t type anything.

✅ Updated:

Clears history

Sets pending_new_chat=True

Thread appears only after typing a message.




Before
if st.sidebar.button('New Chat'):
    reset_chat()   # creates empty thread immediately

After
if st.sidebar.button('New Chat'):
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = None
    st.session_state['pending_new_chat'] = True


No new thread until user types.




8. Sidebar Rendering Order Changed

❌ Original: Sidebar loaded before checking for new thread creation.

🎯 This caused the rename not to reflect immediately.

✅ Updated:

Input field processed before the sidebar

Ensures new chat title appears instantly.



Before

Sidebar rendered BEFORE thread creation logic.

After

Input is captured BEFORE sidebar render:

user_input = st.chat_input("Type here")

# Possibly create thread + title BEFORE sidebar



9. Cleanup of Titles & History

❌ Original: No titles dictionary existed.

❌ Each chat was identified only by UUID.

✅ Updated:

Added thread_titles dictionary to map thread_id → title.

Sidebar shows human-readable chat names.



Before
# No titles stored

After
if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}


Used when creating first message:

short_title = user_input.strip()[:40]
st.session_state['thread_titles'][new_thread_id] = short_title




10. Conversation Switching Logic Improved

❌ Original: Sidebar button showed only UUID and loaded conversation.

❌ Didn’t track titles.

✅ Updated:

Sidebar displays proper titles.

Clicking a title immediately loads the correct history.



Before
if st.sidebar.button(str(thread_id)):
    st.session_state['thread_id'] = thread_id

After
if st.sidebar.button(title, key=f"thread-btn-{thread_id}"):
    st.session_state['thread_id'] = thread_id
    st.session_state['pending_new_chat'] = False




11. Removed Storing Dummy Titles

❌ Original: No title mechanism existed.

❌ Titles like “New chat” were unavoidable.


Before (Original Sidebar)
for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id


➡️ There was no title, so the sidebar always showed UUIDs.
➡️ You also created a thread immediately on "New Chat", causing placeholder entries.


CHANGE 1 — Added a thread_titles dictionary
After
if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}


CHANGE 2 — First message sets the title
After
if user_input and (st.session_state['pending_new_chat'] or st.session_state['thread_id'] is None):
    new_thread_id = generate_thread_id()
    st.session_state['thread_id'] = new_thread_id

    short_title = user_input.strip()
    if len(short_title) > 40:
        short_title = short_title[:37] + "..."

    st.session_state['thread_titles'][new_thread_id] = short_title


CHANGE 3 — Sidebar now shows titles (NOT UUIDs)
Before
st.sidebar.button(str(thread_id))

After
title = st.session_state['thread_titles'].get(thread_id, str(thread_id))
st.sidebar.button(title, key=f"thread-btn-{thread_id}")

✅ Updated: Titles exist only for threads that have at least one user query.

12. Prevented Duplicate Threads

❌ Original: New threads could be added multiple times.

✅ Updated: Checks ensure each thread_id appears only once



Before
add_thread(thread_id)

After
if new_thread_id not in st.session_state['chat_threads']:
    st.session_state['chat_threads'].append(new_thread_id)

############################################################################################################

