import streamlit as st
import datetime
import json
from google import genai
from google.genai import types

st.set_page_config(page_title="Universal Course Generator", layout="wide", page_icon="🎓")

st.title("🎓 Universal Course & Exam Generator (Free Tier)")
st.write("Generate a custom, structured curriculum for **any subject** with assignments, open-response prompts, and comprehensive tests based on your deadline.")

# Sidebar Configuration
st.sidebar.header("Course Parameters")
course_name = st.sidebar.text_input("Course Topic / Subject", placeholder="e.g., Organic Chemistry, Macroeconomics, IB Math HL")
target_date = st.sidebar.date_input("Target Completion Date", min_value=datetime.date.today() + datetime.timedelta(days=7))
num_modules = st.sidebar.slider("Number of Modules", min_value=2, max_value=12, value=4)
api_key = st.sidebar.text_input("Google Gemini API Key (Free from AI Studio)", type="password")

days_remaining = (target_date - datetime.date.today()).days
weeks_remaining = max(1, days_remaining // 7)

st.sidebar.info(f"⏳ **Schedule:** {days_remaining} days (~{weeks_remaining} weeks) remaining to complete the course.")

def build_course_prompt(topic, modules, days):
    return f"""
    Create a detailed, high-rigor educational course on '{topic}' to be completed in {days} days across {modules} modules.
    Provide output STRICTLY as a valid JSON object matching this structure:
    {{
      "course_title": "{topic}",
      "modules": [
        {{
          "module_number": 1,
          "title": "Module Title",
          "estimated_days": {days // modules},
          "lesson": "In-depth theory breakdown, core formulas, key concepts, and detailed explanations.",
          "assignment": {{
            "instructions": "Detailed practical assignment or problem set.",
            "open_response_prompts": [
              "Detailed analytical prompt 1 requiring written explanation.",
              "Detailed analytical prompt 2 requiring critical evaluation or derivation."
            ]
          }},
          "test": {{
            "multiple_choice": [
              {{"question": "Q1", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Option A", "explanation": "Why Option A is correct."}}
            ],
            "open_response_exam": [
              {{"question": "Comprehensive exam question requiring step-by-step mathematical or analytical proof.", "rubric": "Grading criteria."}}
            ]
          }}
        }}
      ]
    }}
    """

if st.button("🚀 Generate Complete Course", type="primary"):
    if not course_name:
        st.error("Please enter a course topic first!")
    elif not api_key:
        st.warning("Please enter your free Google Gemini API Key in the sidebar.")
    else:
        with st.spinner("Building custom curriculum, open-response prompts, and comprehensive assessments..."):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=build_course_prompt(course_name, num_modules, days_remaining),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                course_data = json.loads(response.text)
                st.session_state['course_data'] = course_data
                st.success("Course generated successfully!")
            except Exception as e:
                st.error(f"Error generating course: {str(e)}")

# Display Generated Course
if 'course_data' in st.session_state:
    data = st.session_state['course_data']
    st.header(f"📚 {data.get('course_title', course_name)}")
    
    tabs = st.tabs([f"Module {m['module_number']}: {m['title']}" for m in data.get('modules', [])])
    
    for idx, module in enumerate(data.get('modules', [])):
        with tabs[idx]:
            st.caption(f"⏱️ Suggested Timeline: Complete within {module.get('estimated_days', 7)} days")
            
            # Lesson Section
            st.subheader("📖 In-Depth Lesson & Theory")
            st.write(module.get('lesson', ''))
            
            st.divider()
            
            # Assignment Section
            st.subheader("📝 Module Assignment")
            st.markdown(module.get('assignment', {}).get('instructions', ''))
            
            st.markdown("#### 💬 Open-Response Writing Prompts")
            for i, prompt in enumerate(module.get('assignment', {}).get('open_response_prompts', []), 1):
                st.markdown(f"**Prompt {i}:** {prompt}")
                st.text_area(f"Your Answer (Prompt {i})", key=f"ans_{idx}_{i}")
            
            st.divider()
            
            # Test Section
            st.subheader("⚡ Comprehensive Assessment")
            
            st.markdown("#### Section A: Multiple Choice")
            for q_idx, q in enumerate(module.get('test', {}).get('multiple_choice', []), 1):
                st.write(f"**Q{q_idx}: {q['question']}**")
                user_ans = st.radio(f"Select answer for Q{q_idx}", q['options'], key=f"mcq_{idx}_{q_idx}")
                if st.button(f"Check Q{q_idx}", key=f"btn_mcq_{idx}_{q_idx}"):
                    if user_ans == q['answer']:
                        st.success(f"Correct! {q.get('explanation', '')}")
                    else:
                        st.error(f"Incorrect. Correct answer: {q['answer']}. {q.get('explanation', '')}")
            
            st.markdown("#### Section B: Open-Response / Extended Exam Questions")
            for eq_idx, eq in enumerate(module.get('test', {}).get('open_response_exam', []), 1):
                st.write(f"**Exam Question {eq_idx}:** {eq['question']}")
                st.text_area(f"Write your extended solution/essay for Question {eq_idx}", key=f"exam_ans_{idx}_{eq_idx}")
                with st.expander(f"View Grading Rubric / Model Solution for Q{eq_idx}"):
                    st.write(eq.get('rubric', ''))
