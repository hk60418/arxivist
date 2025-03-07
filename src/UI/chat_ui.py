"""TODO after agent framework."""
import streamlit as st
import time


def chat_ui(generate_response):
    """
    Chat UI for a local AI model using Streamlit.

    Args:
        generate_response (function): A function that takes a user query and returns a response.
    """

    st.set_page_config(page_title="Local AI Chat", layout="wide")
    st.title("💬 Local AI Chat")
    st.caption("Running completely on your machine.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask me something..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt)  # Call the response function
                time.sleep(1)  # Simulate processing delay
                st.markdown(response)

        # Store response
        st.session_state.messages.append({"role": "assistant", "content": response})
