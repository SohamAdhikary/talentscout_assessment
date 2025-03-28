import streamlit as st
import openai
import os
from textblob import TextBlob

# Set your OpenAI API key from the environment
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_questions_with_openai(tech_stack, experience, desired_position, conversation_history):
    """Generates technical interview questions using OpenAI's GPT model based on user input and conversation history."""
    try:
        prompt = (f"Based on the following conversation: {conversation_history}\n"
                  f"Generate 3 technical interview questions for a {desired_position} role "
                  f"with {experience} years of experience in {tech_stack}.")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful interviewer."},
                {"role": "user", "content": prompt}
            ],
            n=1,
            max_tokens=150,
            temperature=0.7
        )
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split("\n") if q.strip()]
        return questions[:5]  # Limit to 5 questions
    except Exception as e:
        st.error(f"Error generating questions: {e}. Please try again.")
        return []

def analyze_sentiment(text):
    """Analyzes the sentiment of a given text."""
    blob = TextBlob(text)
    return blob.sentiment.polarity

def main():
    """Main function to run the Streamlit application."""
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
            st.write(f"Sentiment analysis score of your name: {sentiment_score:.2f}")
            st.session_state.history.append({
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "experience": experience,
                "desired_position": desired_position,
                "location": location,
                "tech_stack": tech_stack
            })
            st.success("Your information has been submitted successfully.")

            # Update conversation history
            st.session_state.conversation += f"User: Name={full_name}, Tech={tech_stack}, Position={desired_position}.\n"

            # Generate questions only if tech_stack and desired_position are provided
            if tech_stack and desired_position:
                questions = generate_questions_with_openai(tech_stack, experience, desired_position, st.session_state.conversation)
                if questions:
                    st.write("Technical Questions:")
                    for q in questions:
                        st.write(f"- {q}")
                        st.session_state.conversation += f"Assistant: {q}\n" #Update conversation with question.

    if st.button("See Previous Inputs"):
        if st.session_state.history:
            st.write("Previous Entries:")
            for entry in st.session_state.history:
                st.write(f"{entry['full_name']} - {entry['tech_stack']} ({entry['desired_position']})")
        else:
            st.write("No previous entries found.")

    if not full_name:
        st.write("Please provide your full name to proceed.")

    if full_name:
        st.write(f"Hello, {full_name}! Let's get started.")

    # Fallback Mechanism for unexpected user input.
    user_input = st.text_input("Ask a follow up question or type 'exit'.")
    if user_input:
        if "exit" in user_input.lower():
            st.stop()
        else:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful interviewer."},
                        {"role": "user", "content": f"{st.session_state.conversation}\nUser: {user_input}"}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                bot_response = response.choices[0].message.content.strip()
                st.write(bot_response)
                st.session_state.conversation += f"User: {user_input}\nAssistant: {bot_response}\n"
            except Exception as e:
                st.error(f"Error: {e}. I am unable to process your request.")

# Data Handling: Streamlit session state is cleared on browser close.
# No explicit data storage is implemented beyond session state.

if __name__ == "__main__":
    main()