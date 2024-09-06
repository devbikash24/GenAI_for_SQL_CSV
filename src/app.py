import streamlit as st
from utilities.uploadFile import UploadFile
import os
from utilities.chatbot import ChatBot

def save_uploaded_file(uploaded_file):
    temp_dir = "data/for_uploads"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def format_message(input_message, bot_message):
    """
    Format the chat message with appropriate styling for both user and bot messages.
    Use <pre> to preserve formatting of user input.
    """
    user_message = f"<div class='message user-message'><img src='https://cdn.truelancer.com/user-picture/519372-5b2608b581c31.jpg' class='chat-icon'>{input_message}</div>"
    bot_message = f"<div class='message bot-message'>{bot_message}<img src='https://st3.depositphotos.com/8950810/17657/v/450/depositphotos_176577870-stock-illustration-cute-smiling-funny-robot-chat.jpg' style='margin-left: 10px;'  class='chat-icon'></div>"
    return user_message + bot_message


def main():

    

    st.set_page_config(page_title="Q&A and RAG with SQL and Tabular Data", layout="wide")
    st.sidebar.header("Settings")
    uploaded_files = st.sidebar.file_uploader("Upload CSV or XLSX files", type=['csv', 'xlsx'], accept_multiple_files=True)
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
    reset_button = st.sidebar.button("Reset Chat")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

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
                height: 30px;
                vertical-align: middle;
                border-radius: 50%;
                margin-right: 10px;
            }
        </style>
        """, unsafe_allow_html=True)

    chat_placeholder = st.empty()
    
    # Display formatted chat history
    if st.session_state.chat_history:
        formatted_history = [format_message(chat["input"], chat["bot"]) for chat in st.session_state.chat_history]
        chat_placeholder.markdown("<div class='chat-messages'>" + "".join(formatted_history) + "</div>", unsafe_allow_html=True)

    input_text = st.text_area("Enter text and press enter:", height=150)
    submit_text = st.button("Submit Text")

    if submit_text and input_text:
        
        # Append the user input and bot response to chat_history
        message, bot_response = ChatBot.respond(st.session_state.chat_history, input_text, chat_type, app_functionality)
        # bot_response = "This is a sample bot response"  # Replace with actual bot logic
        # st.session_state.chat_history.append({"input": message, "bot": bot_response})
        
        # Update the chat display
        chat_placeholder.empty()
        formatted_history = [format_message(chat["input"], chat["bot"]) for chat in st.session_state.chat_history]
        chat_placeholder.markdown("<div class='chat-messages'>" + "".join(formatted_history) + "</div>", unsafe_allow_html=True)

        print(st.session_state.chat_history)

    if uploaded_files and app_functionality == "Process files":
        file_paths = [save_uploaded_file(uploaded_file) for uploaded_file in uploaded_files]
        response, chat_history = UploadFile.run_pipeline(file_paths, st.session_state.chat_history, app_functionality)
        bot_response = response  # Assuming response contains the bot's message for the file processing
        chat_placeholder.empty()
        formatted_history = [format_message(chat["input"], chat["bot"]) for chat in st.session_state.chat_history]
        chat_placeholder.markdown("<div class='chat-messages'>" + "".join(formatted_history) + "</div>", unsafe_allow_html=True)

    if reset_button:
        st.session_state.chat_history = []
        chat_placeholder.empty()

if __name__ == "__main__":
    main()
