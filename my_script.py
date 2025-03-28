import streamlit as st

def main():
    st.title("TalentScout Hiring Assistant")  # Corrected: Indented
    st.write("Welcome! Please provide your details to proceed.")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    experience = st.slider("Years of Experience", 0, 30, 0)
    desired_position = st.text_input("Desired Position(s)")
    location = st.text_input("Current Location")
    tech_stack = st.text_input("Tech Stack (e.g., Python, Django)")

    if st.button("Submit"):
        st.write("Thank you for submitting your information.")

    tech_questions = {
        "Python": ["What is a list comprehension?", "Explain the difference between a list and a tuple."],
        "Django": ["What is a view in Django?", "How do you create a model in Django?"]
    }

    def generate_questions(tech_stack):
        questions = []
        for tech in tech_stack.split(","):
            tech = tech.strip()
            if tech in tech_questions:
                questions.extend(tech_questions[tech])
        return questions[:5]  # Limit to 5 questions

    if tech_stack:
        questions = generate_questions(tech_stack)
        st.write("Technical Questions:")
        for q in questions:
            st.write(f"- {q}")

    if not full_name:
        st.write("Please provide your full name to proceed.")

    if full_name:
        st.write(f"Hello, {full_name}! Let's get started.")
    if st.button("Exit"):
        st.stop()

