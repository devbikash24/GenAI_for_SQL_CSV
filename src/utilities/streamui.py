import streamlit as st

class UISettings:
    """
    Utility class for managing UI settings in Streamlit.
    """
    @staticmethod
    def toggle_sidebar():
        """
        Toggle the visibility state of a UI component (Not applicable in Streamlit by default).
        """
        st.sidebar.empty()
        
    @staticmethod
    def feedback(response):
        """
        Process user feedback on the generated response.

        This method will display feedback buttons (like/dislike) after a bot response.

        Parameters:
            response (str): The chatbot's response for which the feedback is being collected.
        """
        st.write("Did you like this response?")
        col1, col2 = st.columns(2)
        
        with col1:
            # Create a Like button with a unique key for each response
            if st.button("👍 Like", key=f"like_{response}"):
                st.success(f"You liked the response: {response}")
        
        with col2:
            # Create a Dislike button with a unique key for each response
            if st.button("👎 Dislike", key=f"dislike_{response}"):
                st.error(f"You disliked the response: {response}")

