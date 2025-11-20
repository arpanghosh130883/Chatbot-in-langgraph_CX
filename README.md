
# README: Code Changes Summary with Snippets

This README provides a detailed list of all modifications made to the original Streamlit chat application along with corresponding **Before vs After** code snippets for each point.

---

## 1. Thread Creation Logic Modified

### **Before**

```python
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
```

### **After**

```python
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

if 'pending_new_chat' not in st.session_state:
    st.session_state['pending_new_chat'] = True
```

---

## 2. Removed Placeholder Threads

### **Before**

```python
add_thread(st.session_state['thread_id'])
```

### **After**

```python
if user_input and (st.session_state['pending_new_chat'] or st.session_state['thread_id'] is None):
    new_thread_id = generate_thread_id()
    st.session_state['thread_id'] = new_thread_id
    st.session_state['chat_threads'].append(new_thread_id)
```

---

## 3. Thread Title Instead of UUID

### **Before**

```python
st.sidebar.button(str(thread_id))
```

### **After**

```python
title = st.session_state['thread_titles'].get(thread_id, str(thread_id))
st.sidebar.button(title, key=f"thread-btn-{thread_id}")
```

---

## 4. First Query Immediately Sets Title

### **Before**

No mechanism existed.

### **After**

```python
short_title = user_input.strip()
if len(short_title) > 40:
    short_title = short_title[:37] + "..."
st.session_state['thread_titles'][new_thread_id] = short_title
```

---

## 5. Introduction of `pending_new_chat`

### **Before**

Not present.

### **After**

```python
if 'pending_new_chat' not in st.session_state:
    st.session_state['pending_new_chat'] = True
```

---

## 6. Removed `reset_chat()` and `add_thread()`

### **Before**

```python
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
```

### **After**

Both removed and replaced with:

```python
new_thread_id = generate_thread_id()
st.session_state['thread_id'] = new_thread_id
st.session_state['chat_threads'].append(new_thread_id)
```

---

## 7. New Chat Button Behaviour Updated

### **Before**

```python
if st.sidebar.button('New Chat'):
    reset_chat()
```

### **After**

```python
if st.sidebar.button('New Chat'):
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = None
    st.session_state['pending_new_chat'] = True
```

---

## 8. Sidebar Render Order Changed

### **Before**

Sidebar loaded first; input processed after.

### **After**

```python
user_input = st.chat_input('Type here')
# Thread creation handled BEFORE sidebar
```

---

## 9. Added `thread_titles` Dictionary

### **Before**

No storage for titles.

### **After**

```python
if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}
```

---

## 10. Improved Conversation Switching

### **Before**

```python
if st.sidebar.button(str(thread_id)):
    st.session_state['thread_id'] = thread_id
```

### **After**

```python
if st.sidebar.button(title, key=f"thread-btn-{thread_id}"):
    st.session_state['thread_id'] = thread_id
    st.session_state['pending_new_chat'] = False
```

---

## 11. Prevent Duplicate Threads

### **Before**

```python
add_thread(thread_id)
```

### **After**

```python
if new_thread_id not in st.session_state['chat_threads']:
    st.session_state['chat_threads'].append(new_thread_id)
```

---

## 12. Removed Dummy Titles ('New Chat')

### **Before**

```python
st.session_state['thread_titles'][thread_id] = "New chat"
```

### **After**

```python
# Removed completely — titles created ONLY from first user prompt
short_title = user_input.strip()
st.session_state['thread_titles'][new_thread_id] = short_title
```

---

## 13. Sidebar Now Immediately Shows Correct Title

### **Before**

No title mapping existed.

### **After**

```python
title = st.session_state['thread_titles'].get(thread_id, str(thread_id))
st.sidebar.button(title)
```

---

# ✔ Summary

This README documents all improvements made to the chat application including thread creation, title assignment, sidebar updates, and clean removal of unnecessary logic.

