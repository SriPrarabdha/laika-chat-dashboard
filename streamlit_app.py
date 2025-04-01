
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import uuid
import json

# Constants
API_BASE_URL = "https://chat-dashboard-239264243926.us-central1.run.app/"
API_KEY = str(uuid.uuid5(uuid.NAMESPACE_DNS, "laika_dashboard"))

# Page configuration
st.set_page_config(
    page_title="Chat Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-box {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
        cursor: pointer;
    }
    .user-query {
        font-weight: bold;
        margin-bottom: 10px;
    }
    .metadata {
        color: #666;
        font-size: 0.8em;
    }
    .expanded-content {
        background-color: white;
        border: 1px solid #eee;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
        white-space: pre-wrap;
    }
    .crew-log {
        background-color: #f0f7ff;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .crew-response {
        background-color: #f0fff0;
        padding: 10px;
        border-radius: 5px;
    }
    .section-header {
        font-weight: bold;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'date_filter_submitted' not in st.session_state:
    st.session_state.date_filter_submitted = False
if 'expanded_chat' not in st.session_state:
    st.session_state.expanded_chat = None
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Sidebar
st.sidebar.title("Chat Dashboard")
page = st.sidebar.radio("Navigation", ["Index", "Search"])

# Date filter in sidebar
st.sidebar.header("Date Filter")
default_start_date = datetime.now() - timedelta(days=30)
start_date = st.sidebar.date_input("Start Date", default_start_date)
end_date = st.sidebar.date_input("End Date", datetime.now())

def format_date(date):
    """Format date to ISO format string"""
    return date.strftime("%Y-%m-%d")

def apply_date_filter():
    """Set session state when date filter is applied"""
    st.session_state.date_filter_submitted = True
    st.session_state.expanded_chat = None  # Reset expanded chat when filter changes

# Apply date filter button
if st.sidebar.button("Apply Date Filter"):
    apply_date_filter()

# Main content area
if page == "Index":
    st.title("Chat Index")
    
    try:
        # Fetch chats with date filter
        params = {
            "api_key": API_KEY
        }
        
        if st.session_state.date_filter_submitted:
            params["start_date"] = format_date(start_date)
            params["end_date"] = format_date(end_date) + " 23:59:59"
        
        response = requests.get(f"{API_BASE_URL}/chats", params=params)
        
        if response.status_code == 200:
            chats = response.json()
            
            if not chats:
                st.info("No chats found for the selected time period.")
            else:
                # Convert to DataFrame for easier manipulation
                df = pd.DataFrame(chats)
                
                # Sort by created_at in descending order
                df['created_at'] = pd.to_datetime(df['created_at'])
                df = df.sort_values(by='created_at', ascending=False)
                
                # Group by user_chat_id to get unique chats
                unique_chats = df.drop_duplicates(subset=['user_chat_id'])
                
                # Display each unique chat
                for _, chat in unique_chats.iterrows():
                    user_chat_id = chat['user_chat_id']
                    
                    # Fetch messages for this chat
                    texts_response = requests.get(
                        f"{API_BASE_URL}/texts",
                        params={
                            "api_key": API_KEY,
                            "user_chat_id": user_chat_id,
                            "start_date": params.get("start_date"),
                            "end_date": params.get("end_date")
                        }
                    )
                    
                    if texts_response.status_code == 200:
                        texts = texts_response.json()
                        
                        if texts:
                            # Get the latest message
                            latest_message = texts[-1]
                            created_at = pd.to_datetime(latest_message['created_at']).strftime("%Y-%m-%d %H:%M:%S")
                            
                            # Create the chat box
                            chat_box_id = f"chat_{user_chat_id}"
                            
                            # Display the collapsible chat box
                            with st.container():
                                col1, col2 = st.columns([9, 1])
                                
                                # Main content and header
                                with col1:
                                    st.markdown(f"""
                                    <div class="chat-box" id="{chat_box_id}" onclick="this.classList.toggle('expanded')">
                                        <div class="user-query">{latest_message['user_query'][:100] + '...' if len(latest_message['user_query']) > 100 else latest_message['user_query']}</div>
                                        <div class="metadata">ID: {user_chat_id[:10]}... | Created: {created_at}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Expand button
                                with col2:
                                    if st.button("Expand", key=f"btn_{user_chat_id}"):
                                        if st.session_state.expanded_chat == user_chat_id:
                                            st.session_state.expanded_chat = None
                                        else:
                                            st.session_state.expanded_chat = user_chat_id
                            
                            # Show expanded content if this chat is selected
                            if st.session_state.expanded_chat == user_chat_id:
                                st.markdown("<div class='expanded-content'>", unsafe_allow_html=True)
                                
                                # Show all messages in the conversation
                                for idx, message in enumerate(texts):
                                    msg_time = pd.to_datetime(message['created_at']).strftime("%Y-%m-%d %H:%M:%S")
                                    
                                    with st.expander(f"Message {idx+1} - {msg_time}", expanded=idx == len(texts)-1):
                                        st.markdown(f"<div class='user-query'>{message['user_query']}</div>", unsafe_allow_html=True)
                                        
                                        st.markdown("<div class='section-header'>Crew Log:</div>", unsafe_allow_html=True)
                                        st.markdown(f"<div class='crew-log'>{message['crew_log']}</div>", unsafe_allow_html=True)
                                        
                                        st.markdown("<div class='section-header'>Crew Response:</div>", unsafe_allow_html=True)
                                        st.markdown(f"<div class='crew-response'>{message['crew_response']}</div>", unsafe_allow_html=True)
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                
        else:
            st.error(f"Failed to load chats: {response.text}")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif page == "Search":
    st.title("Search Chats")
    
    # Search form
    with st.form(key="search_form"):
        keyword = st.text_input("Search Keyword", key="search_keyword")
        col1, col2 = st.columns(2)
        with col1:
            search_logs = st.checkbox("Search in Crew Logs", value=True)
        with col2:
            search_response = st.checkbox("Search in Crew Responses", value=True)
        
        submit_search = st.form_submit_button("Search")
        
        if submit_search:
            if not keyword:
                st.warning("Please enter a search keyword")
            elif not search_logs and not search_response:
                st.warning("Please select at least one search option")
            else:
                try:
                    # Perform search
                    params = {
                        "api_key": API_KEY,
                        "keyword": keyword,
                        "search_logs": str(search_logs).lower(),
                        "search_response": str(search_response).lower()
                    }
                    
                    response = requests.get(f"{API_BASE_URL}/search", params=params)
                    
                    if response.status_code == 200:
                        st.session_state.search_results = response.json()
                        st.session_state.search_performed = True
                    else:
                        st.error(f"Search failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    # Display search results
    if st.session_state.search_performed:
        if not st.session_state.search_results:
            st.info("No matches found.")
        else:
            st.success(f"Found {len(st.session_state.search_results)} results")
            
            # Convert to DataFrame and sort by date
            df = pd.DataFrame(st.session_state.search_results)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values(by='created_at', ascending=False)
            
            # Display each result
            for idx, result in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([9, 1])
                    
                    # Main content
                    with col1:
                        user_chat_id = result['user_chat_id']
                        created_at = result['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                        
                        st.markdown(f"""
                        <div class="chat-box">
                            <div class="user-query">{result['user_query'][:100] + '...' if len(result['user_query']) > 100 else result['user_query']}</div>
                            <div class="metadata">ID: {user_chat_id[:10]}... | Created: {created_at}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Expand button
                    with col2:
                        if st.button("View", key=f"view_{idx}"):
                            if st.session_state.expanded_chat == idx:
                                st.session_state.expanded_chat = None
                            else:
                                st.session_state.expanded_chat = idx
                
                # Show expanded content if this result is selected
                if st.session_state.expanded_chat == idx:
                    with st.container():
                        st.markdown("<div class='expanded-content'>", unsafe_allow_html=True)
                        
                        st.markdown(f"<div class='user-query'>{result['user_query']}</div>", unsafe_allow_html=True)
                        
                        st.markdown("<div class='section-header'>Crew Log:</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='crew-log'>{result['crew_log']}</div>", unsafe_allow_html=True)
                        
                        st.markdown("<div class='section-header'>Crew Response:</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='crew-response'>{result['crew_response']}</div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
if st.sidebar.button("Check Database Connection"):
    try:
        response = requests.get(f"{API_BASE_URL}/db-info", params={"api_key": API_KEY})
        if response.status_code == 200:
            info = response.json()
            st.sidebar.success(f"Database connected!")
            st.sidebar.info(f"Server time: {info['current_time']}")
            st.sidebar.info(f"PostgreSQL version: {info['postgresql_version']}")
        else:
            st.sidebar.error("Failed to connect to database")
    except Exception as e:
        st.sidebar.error(f"Connection error: {str(e)}")