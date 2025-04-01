import streamlit as st
import requests
import datetime
import uuid

API_URL = "https://chat-dashboard-239264243926.us-central1.run.app/"
# API_URL = "http://0.0.0.0:8000"  # Replace with your API URL

def get_chats_from_api(start_date=None, end_date=None, api_key=None):
    params = {"api_key": api_key}
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    response = requests.get(f"{API_URL}/chats", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching chats: {response.status_code} - {response.text}")
        return []

def get_texts_from_api(user_chat_id=None, user_id=None, chat_id=None, start_date=None, end_date=None, api_key=None):
    params = {"api_key": api_key}
    if user_chat_id:
        params["user_chat_id"] = user_chat_id
    elif user_id and chat_id:
        params["user_id"] = user_id
        params["chat_id"] = chat_id
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    response = requests.get(f"{API_URL}/texts", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching texts: {response.status_code} - {response.text}")
        return []

def search_chats_from_api(keyword, search_logs, search_response, api_key):
    params = {"keyword": keyword, "search_logs": search_logs, "search_response": search_response, "api_key": api_key}
    response = requests.get(f"{API_URL}/search", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error searching chats: {response.status_code} - {response.text}")
        return []

def main():
    st.title("Crew Dashboard")
    api_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, "laika_dashboard"))

    # Sidebar options
    option = st.sidebar.radio("Select Option", ("Index", "Search"))

    start_date = st.sidebar.date_input("Start Date", value=None)
    end_date = st.sidebar.date_input("End Date", value=None)

    if option == "Index":
        filter_type = st.sidebar.selectbox("Filter by", ("user_id", "chat_id", "user_chat_id"))
        chats = get_chats_from_api(start_date=start_date, end_date=end_date, api_key=api_key)

        if filter_type == "user_chat_id":
            user_chat_ids = sorted(list(set(chat["user_chat_id"] for chat in chats)), key=lambda x: next((c["created_at"] for c in chats if c["user_chat_id"] == x), ''))
            selected_user_chat_id = st.sidebar.selectbox("Select user_chat_id", user_chat_ids)

            if selected_user_chat_id:
                texts = get_texts_from_api(user_chat_id=selected_user_chat_id, start_date=start_date, end_date=end_date, api_key=api_key)
                for text in texts:
                    st.write(f"Created At: {text['created_at']}")
                    st.write(f"User Query: {text['user_query']}")
                    st.write(f"Crew Log: {text['crew_log']}")
                    st.write(f"Crew Response: {text['crew_response']}")
                    st.write("---")

        elif filter_type == "user_id" or filter_type == "chat_id":
            unique_ids = sorted(list(set(chat[filter_type] for chat in chats)))
            selected_id = st.sidebar.selectbox(f"Select {filter_type}", unique_ids)
            if selected_id:
                if filter_type == "user_id":
                    chat_ids = sorted(list(set(chat["chat_id"] for chat in chats if chat["user_id"] == selected_id)))
                    selected_chat_id = st.sidebar.selectbox("Select chat_id", chat_ids)
                    if selected_chat_id:
                        texts = get_texts_from_api(user_id=selected_id, chat_id=selected_chat_id, start_date=start_date, end_date=end_date, api_key=api_key)
                        for text in texts:
                            st.write(f"Created At: {text['created_at']}")
                            st.write(f"User Query: {text['user_query']}")
                            st.write(f"Crew Log: {text['crew_log']}")
                            st.write(f"Crew Response: {text['crew_response']}")
                            st.write("---")

    elif option == "Search":
        keyword = st.text_input("Enter keyword to search")
        search_logs = st.checkbox("Search Crew Logs", value=True)
        search_response = st.checkbox("Search Crew Responses", value=True)

        if keyword:
            results = search_chats_from_api(keyword, search_logs, search_response, api_key)
            for result in results:
                st.write(f"Created At: {result['created_at']}")
                st.write(f"User ID: {result['user_id']}")
                st.write(f"Chat ID: {result['chat_id']}")
                st.write(f"User Chat ID: {result['user_chat_id']}")
                st.write(f"User Query: {result['user_query']}")
                st.write(f"Crew Log: {result['crew_log']}")
                st.write(f"Crew Response: {result['crew_response']}")
                st.write("---")

if __name__ == "__main__":
    main()