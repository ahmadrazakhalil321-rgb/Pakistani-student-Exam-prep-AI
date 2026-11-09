
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Page Configuration
st.set_page_config(
    page_title="PakExam AI Prep - Matric & Inter",
    page_icon="📚",
    layout="wide"
)

# Sidebar for Configuration
st.sidebar.title("⚙️ Configuration")
api_key_input = st.sidebar.text_input("Enter Gemini API Key", type="password")

language_choice = st.sidebar.selectbox(
    "Select Explanation Language",
    ["English", "Roman Urdu", "Urdu (اردو)"]
)

st.sidebar.markdown("---")
st.sidebar.info("Upload a chapter PDF or TXT file to get started with board-style exam preparation.")

# Main Title
st.title("🇵🇰 PakExam AI Prep: Smart Chapter Assistant")
st.markdown("Prepare for your Matric and Intermediate exams using your own textbook chapters!")

# Initialize API
if api_key_input:
    genai.configure(api_key=api_key_input)
else:
    # Fallback to Streamlit secrets if hosted on Streamlit Cloud
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.warning("⚠️ Please enter your Gemini API Key in the sidebar or set it in Streamlit Secrets.")

# File Uploader
uploaded_file = st.file_uploader("Upload Chapter File (PDF or TXT)", type=["pdf", "txt"])

@st.cache_data
-def extract_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    else:
        text = uploaded_file.read().decode("utf-8")
    return text

if uploaded_file is not None:
    with st.spinner("Extracting text from chapter..."):
        chapter_text = extract_text(uploaded_file)
    
    st.success(f"Successfully loaded chapter! ({len(chapter_text)} characters extracted)")

    # Tabs for different features
    tab1, tab2 = st.tabs(["📝 Generate Practice Questions", "💡 Answer Checker & Explainer"])

    # --- TAB 1: QUESTION GENERATOR ---
    with tab1:
        st.subheader("Generate Board-Style Questions")
        col1, col2 = st.columns(2)
        
        with col1:
            q_type = st.selectbox("Question Type", ["Multiple Choice Questions (MCQs)", "Short Questions", "Long/Essay Questions"])
        with col2:
            num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
            
        if st.button("Generate Questions"):
            if not api_key_input and "GEMINI_API_KEY" not in st.secrets:
                st.error("Please provide a Gemini API Key.")
            else:
                with st.spinner("Generating questions based on Pakistani board patterns..."):
                    prompt = f"""
                    You are an expert examiner for Pakistani Matric and Intermediate boards (FBISE / Punjab / KP Boards).
                    Based on the following chapter text, generate {num_questions} {q_type}.
                    Respond in {language_choice}. Make sure the questions test conceptual and board-exam patterns.
                    
                    Chapter Text:
                    {chapter_text[:15000]}
                    """
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(prompt)
                        st.markdown("### Generated Practice Questions:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error generating questions: {e}")

    # --- TAB 2: ANSWER CHECKER ---
    with tab2:
        st.subheader("Check Your Answer Against the Chapter")
        user_question = st.text_input("Enter the question you are trying to answer:")
        user_answer = st.text_area("Write your answer here:")
        
        if st.button("Evaluate My Answer"):
            if not user_question or not user_answer:
                st.warning("Please enter both the question and your answer.")
            elif not api_key_input and "GEMINI_API_KEY" not in st.secrets:
                st.error("Please provide a Gemini API Key.")
            else:
                with st.spinner("Evaluating your answer against the textbook..."):
                    prompt = f"""
                    You are an expert Pakistani board teacher. Evaluate the student's answer using the provided chapter text.
                    
                    Question: {user_question}
                    Student's Answer: {user_answer}
                    
                    Provide constructive feedback, correct any factual mistakes based strictly on the text, and give a model answer in {language_choice}.
                    
                    Chapter Text Excerpt:
                    {chapter_text[:15000]}
                    """
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(prompt)
                        st.markdown("### 📊 Evaluation & Explanation:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error evaluating answer: {e}")
else:
    st.info("👆 Please upload a textbook chapter (PDF or TXT) to begin.")
