import streamlit as st
import openai
import os
from textblob import TextBlob

# Set your OpenAI API key from the environment
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_questions_with_openai(tech_stack, experience, desired_position, conversation_history):
    """
    Generates technical interview questions using OpenAI's GPT model based on user input and conversation history.

    Args:
        tech_stack (str): The tech stack specified by the user.
        experience (int): The years of experience specified by the user.
        desired_position (str): The desired position specified by the user.
        conversation_history (str): The conversation history.

    Returns:
        list: A list of generated technical interview questions.
        str: An error message if question generation fails.
    """
    try:
        prompt = (f"Based on the following conversation: {conversation_history}\n"
                  f"Generate 5 technical interview questions for a {desired_position} role "
                  f"with {experience} years of experience in {tech_stack}.")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful interviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,  # Increased max_tokens for longer questions
            temperature=0.7
        )
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split("\n") if q.strip()]
        return questions[:5]
    except Exception as e:
        return f"Error generating questions: {e}. Please try again."

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text.

    Args:
        text (str): The text to analyze.

    Returns:
        float: The sentiment polarity of the text.
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity

def main():
    """
    Main function to run the Streamlit application.
    """
    st.title("TalentScout Hiring Assistant")
    st.write("Welcome! Please provide your details to proceed.")

    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'conversation' not in st.session_state:
        st.session_state.conversation = ""

    # Input fields
    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    experience = st.slider("Years of Experience", 0, 30, 0)
    desired_position = st.text_input("Desired Position(s)")
    location = st.text_input("Current Location")
    tech_stack = st.text_input("Tech Stack (e.g., Python, Django)")

    if st.button("Submit"):
        if not full_name or not email or not phone or not tech_stack:
            st.error("Please fill in all required fields.")
        else:
            sentiment_score = analyze_sentiment(full_name)
            st.markdown("<h3 style='color: green;'>Information Submitted Successfully!</h3>", unsafe_allow_html=True)
            st.markdown("<p>Reviewing Details...</p>", unsafe_allow_html=True)
            st.write(f"Sentiment Analysis: {'Positive' if sentiment_score > 0 else 'Negative' if sentiment_score < 0 else 'Neutral'} ({sentiment_score:.2f})")
            st.write("Submitted Information:")
            st.write(f"Full Name: {full_name}")
            st.write(f"Email: {email}")
            st.write(f"Phone: {phone}")
            st.write(f"Years of Experience: {experience}")
            st.write(f"Desired Position: {desired_position}")
            st.write(f"Location: {location}")
            st.write(f"Tech Stack: {tech_stack}")
            st.session_state.history.append({
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "experience": experience,
                "desired_position": desired_position,
                "location": location,
                "tech_stack": tech_stack
            })
            st.session_state.conversation += f"User: Name={full_name}, Tech={tech_stack}, Position={desired_position}.\n"

            if tech_stack and desired_position:
                st.write(f"Generating technical questions based on {tech_stack}...")
                questions = generate_questions_with_openai(tech_stack, experience, desired_position, st.session_state.conversation)
                if isinstance(questions, list): #check if questions is a list, if not, it is an error message.
                    st.markdown("<h3 style='color: blue;'>Technical Questions:</h3>", unsafe_allow_html=True)
                    for i, q in enumerate(questions):
                        st.write(f"{i+1}. {q}")
                        st.session_state.conversation += f"Assistant: {q}\n"
                else:
                    st.error(questions) #display error message.

    if st.button("See Previous Inputs"):
        if st.session_state.history:
            st.markdown("<h3 style='color: purple;'>Previous Entries:</h3>", unsafe_allow_html=True)
            for entry in st.session_state.history:
                st.write(f"Name: {entry['full_name']}, Tech: {entry['tech_stack']}, Position: {entry['desired_position']}")
        else:
            st.write("No previous entries found.")

    if not full_name:
        st.write("Please provide your full name to proceed.")

    if full_name:
        st.write(f"Hello, {full_name}! Let's get started.")

    user_input = st.text_input("Ask a follow up question or type 'exit'.")
    if user_input:
        if "exit" in user_input.lower():
            st.stop()
        else:
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful interviewer."},
                        {"role": "user", "content": f"{st.session_state.conversation}\nUser: {user_input}"}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                bot_response = response.choices[0].message.content.strip()
                st.write(f"User Question: {user_input}")
                st.write(f"Bot Response: {bot_response}")
                st.session_state.conversation += f"User: {user_input}\nAssistant: {bot_response}\n"
            except Exception as e:
                st.error(f"Error: {e}. I am unable to process your request.")

if __name__ == "__main__":
    main()