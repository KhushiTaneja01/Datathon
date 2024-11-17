# chat_component.py
import openai
import streamlit as st

# Function to display the chat interface with a custom context summary
def chat_interface(context_summary):
    # Set your OpenAI API key securely (replace "YOUR_OPENAI_API_KEY" with your key)

    # Initialize session state variables
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    if "context_added" not in st.session_state:
        st.session_state.context_added = False

    # Initialize a session state variable for the input text
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    # Button in the sidebar to toggle the chat dialog
    if st.sidebar.button("💬 Let's Chat"):
        # Toggle chat visibility
        st.session_state.chat_open = not st.session_state.chat_open

        # Add the initial context summary as a system message only once
        if st.session_state.chat_open and not st.session_state.context_added:
            # Add the context as a "system" message
            print(context_summary)
            st.session_state.messages.insert(0, {"role": "system", "content": context_summary})
            st.session_state.context_added = True

    # Display the chat interface in the sidebar if it is open
    if st.session_state.chat_open:
        with st.sidebar:
            st.title("Ask Bot")

            # Display chat history (excluding the "system" message)
            for message in st.session_state.messages:
                if message["role"] != "system":  # Exclude the system message from display
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Handle user input
            input_text = st.text_input("What help do you need?", value=st.session_state.input_text)
            
            if input_text:  # Check if there is any input
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": input_text})
                with st.chat_message("user"):
                    st.markdown(input_text)

                # Clear the input field by resetting the session state
                st.session_state.input_text = ""

                # Generate a response from OpenAI using the updated conversation history
                with st.chat_message("assistant"):
                    # Collect the response text
                    response_text = openai.ChatCompletion.create(
                        model=st.session_state["openai_model"],
                        messages=st.session_state.messages,
                    ).choices[0].message["content"]

                    # Display the response
                    st.markdown(response_text)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
