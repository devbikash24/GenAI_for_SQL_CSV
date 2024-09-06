import streamlit as st
from utilities.uploadFile import UploadFile
from utilities.chatbot import ChatBot
import pandas as pd
import os

def save_uploaded_file(uploaded_file):
    """
    Save the uploaded file temporarily and return the file path.
    """
    temp_dir = "tempDir"  # Directory to save the temporary files
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def main():
    st.set_page_config(page_title="Q&A and RAG with SQL and Tabular Data", layout="wide")

    # Sidebar for controls
    st.sidebar.header("Settings")
    # File uploader in sidebar
    uploaded_files = st.sidebar.file_uploader("Upload CSV or XLSX files", type=['csv', 'xlsx'], accept_multiple_files=True)
    # Dropdown for app functionality and chat type
    app_functionality = st.sidebar.selectbox("App functionality", ["Chat", "Process files"])
    chat_type = st.sidebar.selectbox(
        "Chat type",
        [
            "Q&A with stored SQL-DB",
            "Q&A with stored CSV/XLSX SQL-DB",
            "RAG with stored CSV/XLSX ChromaDB",
            "Q&A with Uploaded CSV/XLSX SQL-DB"
        ]
    )
    # Button to clear the chat history
    reset_button = st.sidebar.button("Reset Chat")

    # Persistent storage for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Add custom styles for chat interface
    st.markdown("""
        <style>
            .chat-messages {
                overflow-y: auto;
                height: 400px;
                padding: 4px;
                border-radius: 10px;
            }
            .message {
                margin: 10px 0;
                padding: 5px;
                border-radius: 10px;
        
            }
            .user-message {
                text-align: left;
            }
            .bot-message {
                text-align: right;
            }
            .chat-icon {
                height: 20px;
                vertical-align: middle;
                border-radius: 50%;
                margin-right: 10px;
            }
        </style>
        """, unsafe_allow_html=True)

    # Display chat history above the input form
    chat_placeholder = st.empty()
    if st.session_state.chat_history:
        chat_placeholder.markdown("<div class='chat-messages'>" + "".join(st.session_state.chat_history) + "</div>", unsafe_allow_html=True)

    # Text input for chat
    input_text = st.text_area("Enter text and press enter:", height=150)
    submit_text = st.button("Submit Text")

    # Handle chat interactions
    if submit_text and input_text:
        user_message = f"<div class='message user-message'><img src='https://st3.depositphotos.com/8950810/17657/v/450/depositphotos_176577870-stock-illustration-cute-smiling-funny-robot-chat.jpg' class='chat-icon'>{input_text}</div>"
        bot_response = f"<div class='message bot-message'>Bot: fwrfwf</div>"
        # bot_response = ChatBot.respond(chat_history, user_input, chat_type, app_functionality)
        st.session_state.chat_history.append(user_message)
        st.session_state.chat_history.append(bot_response)
        chat_placeholder.empty()  # Refresh display
        chat_placeholder.markdown("<div class='chat-messages'>" + "".join(st.session_state.chat_history) + "</div>", unsafe_allow_html=True)

    # Process uploaded files
    # Process uploaded files
    # Process uploaded files
    if uploaded_files and app_functionality == "Process files":
        file_paths = []
        for uploaded_file in uploaded_files:
            file_path = save_uploaded_file(uploaded_file)  # Save the file
            file_paths.append(file_path)  # Add the file path to list

        # Call the run_pipeline function with the saved file paths and chat history
        response, chat_history = UploadFile.run_pipeline(file_paths, st.session_state.chat_history, app_functionality)
        bot_message = f"<div class='message bot-message'>Bot: {response}</div>"
        st.session_state.chat_history = chat_history
        st.session_state.chat_history.append(bot_message)

        # Refresh the chat display
        chat_placeholder.empty()
        chat_placeholder.markdown("<div class='chat-messages'>" + "".join(st.session_state.chat_history) + "</div>", unsafe_allow_html=True)
    # Reset chat history
    if reset_button:
        st.session_state.chat_history = []  # Clear chat history
        chat_placeholder.empty()  # Clear display

if __name__ == "__main__":
    main()
