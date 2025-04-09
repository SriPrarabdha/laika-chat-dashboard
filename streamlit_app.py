
# import streamlit as st
# import requests
# import pandas as pd
# from datetime import datetime, timedelta
# import uuid
# import json

# # Constants
# API_BASE_URL = "https://chat-dashboard-239264243926.us-central1.run.app/"
# API_KEY = str(uuid.uuid5(uuid.NAMESPACE_DNS, "laika_dashboard"))

# # Page configuration
# st.set_page_config(
#     page_title="Chat Dashboard",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     .chat-box {
#         border: 1px solid #ddd;
#         border-radius: 8px;
#         padding: 15px;
#         margin-bottom: 10px;
#         background-color: #f9f9f9;
#         cursor: pointer;
#     }
#     .user-query {
#         font-weight: bold;
#         margin-bottom: 10px;
#     }
#     .metadata {
#         color: #666;
#         font-size: 0.8em;
#     }
#     .expanded-content {
#         background-color: white;
#         border: 1px solid #eee;
#         border-radius: 5px;
#         padding: 10px;
#         margin-top: 10px;
#         white-space: pre-wrap;
#     }
#     .crew-log {
#         background-color: #f0f7ff;
#         padding: 10px;
#         border-radius: 5px;
#         margin-bottom: 10px;
#     }
#     .crew-response {
#         background-color: #f0fff0;
#         padding: 10px;
#         border-radius: 5px;
#     }
#     .section-header {
#         font-weight: bold;
#         margin-bottom: 5px;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Initialize session state variables if they don't exist
# if 'date_filter_submitted' not in st.session_state:
#     st.session_state.date_filter_submitted = False
# if 'expanded_chat' not in st.session_state:
#     st.session_state.expanded_chat = None
# if 'search_performed' not in st.session_state:
#     st.session_state.search_performed = False
# if 'search_results' not in st.session_state:
#     st.session_state.search_results = []

# # Sidebar
# st.sidebar.title("Chat Dashboard")
# page = st.sidebar.radio("Navigation", ["Index", "Search"])

# # Date filter in sidebar
# st.sidebar.header("Date Filter")
# default_start_date = datetime.now() - timedelta(days=30)
# start_date = st.sidebar.date_input("Start Date", default_start_date)
# end_date = st.sidebar.date_input("End Date", datetime.now())

# def format_date(date):
#     """Format date to ISO format string"""
#     return date.strftime("%Y-%m-%d")

# def apply_date_filter():
#     """Set session state when date filter is applied"""
#     st.session_state.date_filter_submitted = True
#     st.session_state.expanded_chat = None  # Reset expanded chat when filter changes

# # Apply date filter button
# if st.sidebar.button("Apply Date Filter"):
#     apply_date_filter()

# # Main content area
# if page == "Index":
#     st.title("Chat Index")
    
#     try:
#         # Fetch chats with date filter
#         params = {
#             "api_key": API_KEY
#         }
        
#         if st.session_state.date_filter_submitted:
#             params["start_date"] = format_date(start_date)
#             params["end_date"] = format_date(end_date) + " 23:59:59"
        
#         response = requests.get(f"{API_BASE_URL}/chats", params=params)
        
#         if response.status_code == 200:
#             chats = response.json()
            
#             if not chats:
#                 st.info("No chats found for the selected time period.")
#             else:
#                 # Convert to DataFrame for easier manipulation
#                 df = pd.DataFrame(chats)
                
#                 # Sort by created_at in descending order
#                 df['created_at'] = pd.to_datetime(df['created_at'])
#                 df = df.sort_values(by='created_at', ascending=False)
                
#                 # Group by user_chat_id to get unique chats
#                 unique_chats = df.drop_duplicates(subset=['user_chat_id'])
                
#                 # Display each unique chat
#                 for _, chat in unique_chats.iterrows():
#                     user_chat_id = chat['user_chat_id']
                    
#                     # Fetch messages for this chat
#                     texts_response = requests.get(
#                         f"{API_BASE_URL}/texts",
#                         params={
#                             "api_key": API_KEY,
#                             "user_chat_id": user_chat_id,
#                             "start_date": params.get("start_date"),
#                             "end_date": params.get("end_date")
#                         }
#                     )
                    
#                     if texts_response.status_code == 200:
#                         texts = texts_response.json()
                        
#                         if texts:
#                             # Get the latest message
#                             latest_message = texts[-1]
#                             created_at = pd.to_datetime(latest_message['created_at']).strftime("%Y-%m-%d %H:%M:%S")
                            
#                             # Create the chat box
#                             chat_box_id = f"chat_{user_chat_id}"
                            
#                             # Display the collapsible chat box
#                             with st.container():
#                                 col1, col2 = st.columns([9, 1])
                                
#                                 # Main content and header
#                                 with col1:
#                                     st.markdown(f"""
#                                     <div class="chat-box" id="{chat_box_id}" onclick="this.classList.toggle('expanded')">
#                                         <div class="user-query">{latest_message['user_query'][:100] + '...' if len(latest_message['user_query']) > 100 else latest_message['user_query']}</div>
#                                         <div class="metadata">ID: {user_chat_id[:10]}... | Created: {created_at}</div>
#                                     </div>
#                                     """, unsafe_allow_html=True)
                                
#                                 # Expand button
#                                 with col2:
#                                     if st.button("Expand", key=f"btn_{user_chat_id}"):
#                                         if st.session_state.expanded_chat == user_chat_id:
#                                             st.session_state.expanded_chat = None
#                                         else:
#                                             st.session_state.expanded_chat = user_chat_id
                            
#                             # Show expanded content if this chat is selected
#                             if st.session_state.expanded_chat == user_chat_id:
#                                 st.markdown("<div class='expanded-content'>", unsafe_allow_html=True)
                                
#                                 # Show all messages in the conversation
#                                 for idx, message in enumerate(texts):
#                                     msg_time = pd.to_datetime(message['created_at']).strftime("%Y-%m-%d %H:%M:%S")
                                    
#                                     with st.expander(f"Message {idx+1} - {msg_time}", expanded=idx == len(texts)-1):
#                                         st.markdown(f"<div class='user-query'>{message['user_query']}</div>", unsafe_allow_html=True)
                                        
#                                         st.markdown("<div class='section-header'>Crew Log:</div>", unsafe_allow_html=True)
#                                         st.markdown(f"<div class='crew-log'>{message['crew_log']}</div>", unsafe_allow_html=True)
                                        
#                                         st.markdown("<div class='section-header'>Crew Response:</div>", unsafe_allow_html=True)
#                                         st.markdown(f"<div class='crew-response'>{message['crew_response']}</div>", unsafe_allow_html=True)
                                
#                                 st.markdown("</div>", unsafe_allow_html=True)
                
#         else:
#             st.error(f"Failed to load chats: {response.text}")
            
#     except Exception as e:
#         st.error(f"An error occurred: {str(e)}")

# elif page == "Search":
#     st.title("Search Chats")
    
#     # Search form
#     with st.form(key="search_form"):
#         keyword = st.text_input("Search Keyword", key="search_keyword")
#         col1, col2 = st.columns(2)
#         with col1:
#             search_logs = st.checkbox("Search in Crew Logs", value=True)
#         with col2:
#             search_response = st.checkbox("Search in Crew Responses", value=True)
        
#         submit_search = st.form_submit_button("Search")
        
#         if submit_search:
#             if not keyword:
#                 st.warning("Please enter a search keyword")
#             elif not search_logs and not search_response:
#                 st.warning("Please select at least one search option")
#             else:
#                 try:
#                     # Perform search
#                     params = {
#                         "api_key": API_KEY,
#                         "keyword": keyword,
#                         "search_logs": str(search_logs).lower(),
#                         "search_response": str(search_response).lower()
#                     }
                    
#                     response = requests.get(f"{API_BASE_URL}/search", params=params)
                    
#                     if response.status_code == 200:
#                         st.session_state.search_results = response.json()
#                         st.session_state.search_performed = True
#                     else:
#                         st.error(f"Search failed: {response.text}")
                        
#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
    
#     # Display search results
#     if st.session_state.search_performed:
#         if not st.session_state.search_results:
#             st.info("No matches found.")
#         else:
#             st.success(f"Found {len(st.session_state.search_results)} results")
            
#             # Convert to DataFrame and sort by date
#             df = pd.DataFrame(st.session_state.search_results)
#             df['created_at'] = pd.to_datetime(df['created_at'])
#             df = df.sort_values(by='created_at', ascending=False)
            
#             # Display each result
#             for idx, result in df.iterrows():
#                 with st.container():
#                     col1, col2 = st.columns([9, 1])
                    
#                     # Main content
#                     with col1:
#                         user_chat_id = result['user_chat_id']
#                         created_at = result['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                        
#                         st.markdown(f"""
#                         <div class="chat-box">
#                             <div class="user-query">{result['user_query'][:100] + '...' if len(result['user_query']) > 100 else result['user_query']}</div>
#                             <div class="metadata">ID: {user_chat_id[:10]}... | Created: {created_at}</div>
#                         </div>
#                         """, unsafe_allow_html=True)
                    
#                     # Expand button
#                     with col2:
#                         if st.button("View", key=f"view_{idx}"):
#                             if st.session_state.expanded_chat == idx:
#                                 st.session_state.expanded_chat = None
#                             else:
#                                 st.session_state.expanded_chat = idx
                
#                 # Show expanded content if this result is selected
#                 if st.session_state.expanded_chat == idx:
#                     with st.container():
#                         st.markdown("<div class='expanded-content'>", unsafe_allow_html=True)
                        
#                         st.markdown(f"<div class='user-query'>{result['user_query']}</div>", unsafe_allow_html=True)
                        
#                         st.markdown("<div class='section-header'>Crew Log:</div>", unsafe_allow_html=True)
#                         st.markdown(f"<div class='crew-log'>{result['crew_log']}</div>", unsafe_allow_html=True)
                        
#                         st.markdown("<div class='section-header'>Crew Response:</div>", unsafe_allow_html=True)
#                         st.markdown(f"<div class='crew-response'>{result['crew_response']}</div>", unsafe_allow_html=True)
                        
#                         st.markdown("</div>", unsafe_allow_html=True)

# # Footer
# st.sidebar.markdown("---")
# if st.sidebar.button("Check Database Connection"):
#     try:
#         response = requests.get(f"{API_BASE_URL}/db-info", params={"api_key": API_KEY})
#         if response.status_code == 200:
#             info = response.json()
#             st.sidebar.success(f"Database connected!")
#             st.sidebar.info(f"Server time: {info['current_time']}")
#             st.sidebar.info(f"PostgreSQL version: {info['postgresql_version']}")
#         else:
#             st.sidebar.error("Failed to connect to database")
#     except Exception as e:
#         st.sidebar.error(f"Connection error: {str(e)}")

 
import streamlit as st
import requests
import uuid
from datetime import datetime, timedelta

# --- Configuration ---
st.set_page_config(
    page_title="Laika Chat Dashboard",
    page_icon="💬",
    layout="wide",
)

# --- Authentication ---
# WARNING: Hardcoding credentials is not secure for production.
# Consider using environment variables, secrets management, or a dedicated auth library.
CORRECT_USERNAME = "laika-admin"
CORRECT_PASSWORD = "Laika@Admin@Dashboard@123"

def check_password():
    """Returns `True` if the user had the correct password."""

    # Initialize authentication status if it doesn't exist
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # If already authenticated, do nothing further here
    if st.session_state["authenticated"]:
        return True

    # --- Login Form ---
    st.markdown("<h1 style='text-align: center;'>Login Required</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please enter your credentials to access the dashboard.</p>", unsafe_allow_html=True)

    login_form = st.empty() # Use a placeholder

    with login_form.form("credentials"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
                st.session_state["authenticated"] = True
                login_form.empty() # Clear the form
                st.success("Login successful!")
                st.rerun() # Rerun the script to show the main app
            else:
                st.error("Incorrect username or password")
                st.session_state["authenticated"] = False # Ensure state is false on failure

    return st.session_state["authenticated"] # Return current auth status

# --- Main Application Logic ---

# Call the authentication check first. If it returns False, stop execution.
if not check_password():
    st.stop() # Stop the app execution if not authenticated

# --- If authenticated, the rest of the app runs ---

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4B5563;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #4B5563;
        margin-top: 1rem;
    }
    .user-message {
        background-color: #f0f4f9;
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
    }
    .bot-message {
        background-color: #e2f0ff;
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
    }
    .timestamp {
        font-size: 0.7rem;
        color: #6B7280;
        text-align: right;
    }
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .stRadio label {
        background-color: #f3f4f6;
        padding: 8px 15px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 5px;
    }
    .stRadio label:hover {
        background-color: #e5e7eb;
    }
    .search-box {
        background-color: #f9fafb;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .divider {
        margin: 20px 0;
        border-top: 1px solid #e5e7eb;
    }
    .sidebar-header {
        margin-top: 20px;
        font-size: 1.2rem;
        font-weight: 600;
        color: #4B5563;
    }
    .chat-button {
        background-color: #f3f4f6;
        padding: 10px 15px;
        border-radius: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        margin: 5px;
        border: 1px solid #e5e7eb;
    }
    .chat-button:hover {
        background-color: #e5e7eb;
    }
    .chat-button.selected {
        background-color: #dbeafe;
        border-color: #3b82f6;
    }
    .date-filter-btn {
        margin-right: 10px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .date-filter-btn.selected {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "https://chat-dashboard-239264243926.us-central1.run.app/"
API_KEY = str(uuid.uuid5(uuid.NAMESPACE_DNS, "laika_dashboard"))

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>💬 Chat Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")
    option = st.radio(
        "Dashboard Mode",
        ["Browse Conversations", "Search Messages"],
        help="Switch between Browse chats or searching for specific messages"
    )
    st.markdown("---") # Separator
    if st.button("Logout", key="logout_button"):
        st.session_state["authenticated"] = False
        st.rerun()

# --- Session State Initialization (for app functionality) ---
if 'selected_chat_id' not in st.session_state:
    st.session_state.selected_chat_id = None
if 'selected_user_id' not in st.session_state:
    st.session_state.selected_user_id = None
if 'conversation_submitted' not in st.session_state:
    st.session_state.conversation_submitted = False
# Add date filter to session state, default to 'today'
if 'date_filter' not in st.session_state:
    st.session_state.date_filter = 'today'

# --- Helper Functions ---
def select_chat(chat_id, user_id):
    st.session_state.selected_chat_id = chat_id
    st.session_state.selected_user_id = user_id

def set_date_filter(filter_name):
    st.session_state.date_filter = filter_name
    st.session_state.selected_chat_id = None
    st.session_state.selected_user_id = None
    st.session_state.conversation_submitted = False

# --- Browse Conversations Mode ---
if option == "Browse Conversations":
    st.markdown("<div class='main-header'>Laika Chat Conversations</div>", unsafe_allow_html=True)
    st.markdown("Explore conversations between users and the AI assistant.")

    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        today_btn = st.button(
            "Today",
            key="today_btn",
            type="primary" if st.session_state.date_filter == 'today' else "secondary",
            use_container_width=True,
            on_click=set_date_filter,
            args=('today',)
        )
    with col2:
        yesterday_btn = st.button(
            "Yesterday",
            key="yesterday_btn",
            type="primary" if st.session_state.date_filter == 'yesterday' else "secondary",
            use_container_width=True,
            on_click=set_date_filter,
            args=('yesterday',)
        )

    now = datetime.now()
    if st.session_state.date_filter == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_date = now.isoformat()
    else:  # yesterday
        yesterday = now - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_date = yesterday.replace(hour=23, minute=59, second=59).isoformat()

    if not st.session_state.conversation_submitted:
        try:
            response = requests.get(
                f"{API_URL}/chats",
                params={
                    "api_key": API_KEY,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            response.raise_for_status()
            chats = response.json()

            if chats:
                unique_chats = {}
                for chat in chats:
                    chat_id = chat["chat_id"]
                    if chat_id not in unique_chats:
                        unique_chats[chat_id] = {
                            "chat_id": chat_id,
                            "user_id": chat["user_id"]
                        }

                chat_data = list(unique_chats.values())

                st.markdown(f"<div class='sub-header'>Select Conversation ({st.session_state.date_filter.title()})</div>", unsafe_allow_html=True)
                st.markdown(f"Found {len(chat_data)} unique conversations")

                # Create a container for the grid
                chat_grid = st.container()

                # Create 5-column grid layout
                num_chats = len(chat_data)
                num_rows = (num_chats + 4) // 5

                with chat_grid:
                    for row in range(num_rows):
                        cols = st.columns(5)
                        for col in range(5):
                            idx = row * 5 + col
                            if idx < num_chats:
                                chat = chat_data[idx]
                                chat_id = chat["chat_id"]
                                user_id = chat["user_id"]

                                # Determine if this chat is selected
                                is_selected = (st.session_state.selected_chat_id == chat_id)

                                # Create a checkbox for selection
                                with cols[col]:
                                    checked = st.checkbox(
                                        f"{chat_id[-6:]}",
                                        key=f"chat_{idx}",
                                        value=is_selected,
                                        help=f"User: {user_id}, Chat: {chat_id}"
                                    )
                                    if checked:
                                        # If checked, update the selection, unchecking others is handled implicitly by streamlit rerun
                                        select_chat(chat_id, user_id)
                                    elif is_selected and not checked:
                                        # If currently selected but unchecked by user, clear selection
                                        st.session_state.selected_chat_id = None
                                        st.session_state.selected_user_id = None


                # Display currently selected chat info if any
                if st.session_state.selected_chat_id:
                    st.success(f"Selected: User {st.session_state.selected_user_id} - Chat {st.session_state.selected_chat_id}")

                # Submit button to confirm selection
                if st.button("View Conversation", use_container_width=True):
                    if st.session_state.selected_chat_id:
                        st.session_state.conversation_submitted = True
                        st.rerun()
                    else:
                        st.error("Please select a conversation first.")
            else:
                st.info(f"No chats found for {st.session_state.date_filter}.")

        except requests.RequestException as e:
            st.error(f"Error fetching chats: {e}")

    # Show selected conversation if submitted
    if st.session_state.conversation_submitted and st.session_state.selected_chat_id:
        # Add a button to go back to conversation selection
        if st.button("← Back to Conversation Selection"):
            st.session_state.conversation_submitted = False
            st.session_state.selected_chat_id = None # Clear selection when going back
            st.session_state.selected_user_id = None
            st.rerun()

        # Show the chat information
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style='padding: 15px; background-color: #f9fafb; border-radius: 8px;'>
                <span style='font-weight: 600; color: #4B5563;'>User ID:</span> {st.session_state.selected_user_id}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style='padding: 15px; background-color: #f9fafb; border-radius: 8px;'>
                <span style='font-weight: 600; color: #4B5563;'>Chat ID:</span> {st.session_state.selected_chat_id}
            </div>
            """, unsafe_allow_html=True)

        # Fetch messages for selected chat
        try:
            with st.spinner("Loading messages..."):
                response = requests.get(
                    f"{API_URL}/texts",
                    params={
                        "api_key": API_KEY,
                        "user_id": st.session_state.selected_user_id,
                        "chat_id": st.session_state.selected_chat_id,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                )
                response.raise_for_status()
                messages = response.json()
        except requests.RequestException as e:
            st.error(f"Error fetching messages: {e}")
            messages = []

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        if not messages:
            st.info("This conversation has no messages.")
        else:
            st.markdown(f"<div class='sub-header'>Conversation</div>", unsafe_allow_html=True)

            # Create a container for the chat with a max height and scrolling
            chat_container = st.container()

            with chat_container:
                for msg in messages:
                    # Format timestamp
                    created_at_dt = datetime.fromisoformat(msg["created_at"].replace("Z", "+00:00"))
                    created_at_str = created_at_dt.strftime("%Y-%m-%d %H:%M:%S")

                    # User Message
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(f"<div class='user-message'>{msg['user_query']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='timestamp'>{created_at_str}</div>", unsafe_allow_html=True)

                    # Bot Response
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(f"<div class='bot-message'>{msg['crew_response']}</div>", unsafe_allow_html=True)
                        with st.expander("View Crew Processing Log"):
                            st.code(msg["crew_log"])
                        st.markdown(f"<div class='timestamp'>{created_at_str}</div>", unsafe_allow_html=True)

# --- Search Messages Mode ---
elif option == "Search Messages":
    st.markdown("<div class='main-header'>Search Conversations</div>", unsafe_allow_html=True)
    st.markdown("Find specific messages across all conversations.")

    # Search controls in a nice container
    with st.container():
        st.markdown("<div class='search-box'>", unsafe_allow_html=True)
        keyword = st.text_input("Enter search keyword", placeholder="Type keywords to search...")

        col1, col2 = st.columns(2)
        with col1:
            search_logs = st.checkbox("Search Crew Processing Logs", value=True)
        with col2:
            search_response = st.checkbox("Search Crew Responses", value=True)

        # Date filter for search as well
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            today_search = st.checkbox("Today", value=True, key="search_today")
        with col2:
            yesterday_search = st.checkbox("Yesterday", value=False, key="search_yesterday")

        search_button = st.button("🔍 Search", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if search_button:
        if not keyword.strip():
            st.error("Please enter a keyword to search for.")
        elif not (search_logs or search_response):
            st.error("Please select at least one search field (Logs or Responses).")
        elif not (today_search or yesterday_search):
            st.error("Please select at least one date filter (Today or Yesterday).")
        else:
            try:
                # Get date ranges for search
                now = datetime.now()
                start_date_search = None
                end_date_search = None

                if today_search and yesterday_search:
                    # Both days selected
                    yesterday = now - timedelta(days=1)
                    start_date_search = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                    end_date_search = now.isoformat()
                elif today_search:
                    # Only today
                    start_date_search = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                    end_date_search = now.isoformat()
                elif yesterday_search:
                    # Only yesterday
                    yesterday = now - timedelta(days=1)
                    start_date_search = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                    end_date_search = yesterday.replace(hour=23, minute=59, second=59).isoformat()

                with st.spinner(f"Searching for '{keyword}'..."):
                    response = requests.get(
                        f"{API_URL}/search",
                        params={
                            "api_key": API_KEY,
                            "keyword": keyword,
                            "search_logs": search_logs,
                            "search_response": search_response,
                            "start_date": start_date_search,
                            "end_date": end_date_search
                        }
                    )
                    response.raise_for_status()
                    results = response.json()
            except requests.RequestException as e:
                st.error(f"Search error: {e}")
                results = [] # Ensure results is defined even on error

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

            if not results:
                st.info(f"No results found for '{keyword}'.")
            else:
                st.markdown(f"<div class='sub-header'>Results for '{keyword}'</div>", unsafe_allow_html=True)
                st.markdown(f"Found {len(results)} matching messages")

                for result in results:
                    created_at_dt = datetime.fromisoformat(result["created_at"].replace("Z", "+00:00"))
                    created_at_str = created_at_dt.strftime("%Y-%m-%d %H:%M:%S")

                    st.markdown(f"""
                    <div style="background-color: #f9fafb; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                        <span style="font-weight: bold;">User:</span> {result['user_id']} |
                        <span style="font-weight: bold;">Chat:</span> {result['chat_id']}
                    </div>
                    """, unsafe_allow_html=True)

                    # User Message
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(f"<div class='user-message'>{result['user_query']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='timestamp'>{created_at_str}</div>", unsafe_allow_html=True)

                    # Bot Response
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(f"<div class='bot-message'>{result['crew_response']}</div>", unsafe_allow_html=True)
                        with st.expander("View Crew Processing Log"):
                            st.code(result["crew_log"])
                        st.markdown(f"<div class='timestamp'>{created_at_str}</div>", unsafe_allow_html=True)

                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# --- Footer (runs only if authenticated) ---
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 10px; color: #6B7280; font-size: 0.8rem;">
    Laika Chat Dashboard • Analytics & Monitoring Tool
</div>
""", unsafe_allow_html=True)