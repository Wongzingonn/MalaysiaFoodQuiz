import os
import streamlit as st
from PIL import Image

# Define text files path
base_path = os.path.dirname(__file__)
questions_path = os.path.join(base_path, "Questions.txt")
answers_path = os.path.join(base_path, "Answers.txt")

with open(questions_path, "r") as txt:
    questions = txt.readlines()

# Data splitting
def data_split(line: str) -> tuple:
    data = line.strip().split(":")
    qid = data[0]
    correct = data[1]
    question = data[2]
    optionA = data[3]
    optionB = data[4]
    optionC = data[5]
    optionD = data[6]
    return qid, correct, question, optionA, optionB, optionC, optionD

# Append answer to Answers.txt
def append_answer(name: str, qid: str, user_answer: str):
    with open(answers_path, "a") as output:
        output.write(f"{name},{qid},{user_answer}\n")

# Get aggregate statistics from Answers.txt
@st.cache_data
def get_aggregate_stats(answers_file: str, correct_answers_dict: dict) -> tuple:
    marks_per_question = {qid: 0 for qid in correct_answers_dict.keys()}
    total_quiz_marks = 0
    
    if os.path.exists(answers_file):
        with open(answers_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) == 3:
                    _, qid, ans = parts
                    # Ensure qid exists in the current question set
                    if qid in correct_answers_dict:
                        if correct_answers_dict[qid] == ans:
                            marks_per_question[qid] += 1
                            total_quiz_marks += 1
                            
    return marks_per_question, total_quiz_marks

# Extract correct answers mapping for aggregate stats calculation
correct_answers_map = {}
for line in questions:
    qid, correct, _, _, _, _, _ = data_split(line)
    correct_answers_map[qid] = correct

st.title("Malaysian Food Quiz")

if st.session_state.get('quit', False):
    st.subheader("Goodbye!")
    st.write("Thank you for participating in the Malaysian Food Quiz. You may now close this tab.")
    if st.button("Start New Quiz"):
        st.session_state.clear()
        st.rerun()
    st.stop()

name = st.text_input("Enter your name")

# Main quiz flow
if name:

    st.write(f"Welcome to the quiz, **{name}**!")

    if 'current_q' not in st.session_state:
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.answers = {}

    if st.session_state.current_q < len(questions):
        line = questions[st.session_state.current_q]
        qid, correct, question, optionA, optionB, optionC, optionD = data_split(line)
        question_number = st.session_state.current_q + 1

        st.subheader(f"Question {question_number} of {len(questions)}")
        st.write(question)

        if question_number == 3 or question_number == 4:

            img_path = os.path.join(base_path, "imgs", f"q{qid}.jpg")

            if os.path.exists(img_path):
                image = Image.open(img_path)
                st.image(image, caption=f"Image for Question {question_number}")
            else:
                st.warning("Image not found")

        options = {
            "A": optionA,
            "B": optionB,
            "C": optionC,
            "D": optionD
        }

        is_answered = qid in st.session_state.answers

        st.radio(
            "Choose your answer:",
            options.keys(),
            format_func=lambda x: f"{x}. {options[x]}",
            key=f"radio_{qid}",
            disabled=is_answered
        )

        if is_answered:
            ans_data = st.session_state.answers[qid]
            if ans_data['is_correct']:
                st.success("Correct!")
            else:
                st.error(f"Wrong! The correct answer is {ans_data['correct']}.")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.session_state.current_q > 0:
                def go_prev():
                    st.session_state.current_q -= 1
                st.button("Previous", on_click=go_prev)

        with col2:
            if not is_answered:
                def submit_answer():
                    ans = st.session_state[f"radio_{qid}"]
                    append_answer(name, qid, ans)
                    is_correct = (ans == correct)
                    if is_correct:
                        st.session_state.score += 1
                    
                    st.session_state.answers[qid] = {
                        "correct": correct,
                        "user_answer": ans,
                        "is_correct": is_correct
                    }
                st.button("Submit Answer", on_click=submit_answer)

        with col3:
            def go_next():
                st.session_state.current_q += 1
                
            if st.session_state.current_q < len(questions) - 1:
                st.button("Next", on_click=go_next)
            else:
                st.button("See Results", on_click=go_next)

    else:
        st.subheader("Quiz Complete!")
        
        # Build summary table data
        summary_data = []
        for line in questions:
            q_id, correct_ans, q_text, _, _, _, _ = data_split(line)
            if q_id in st.session_state.answers:
                res = st.session_state.answers[q_id]
                user_ans = res['user_answer']
                is_correct = "✅ Correct" if res['is_correct'] else "❌ Wrong"
            else:
                user_ans = "Not answered"
                is_correct = "❌ Wrong"
                
            summary_data.append({
                "Question No.": q_id,
                "Your Answer": user_ans,
                "Correct Answer": correct_ans,
                "Result": is_correct
            })
            
        st.write(f"### {name}'s Results Summary")
        st.table(summary_data)
                
        st.subheader(f"Your Final Score: {st.session_state.score} / {len(questions)}")
        
        st.divider()
        
        # Aggregate statistics
        st.subheader("Aggregate Statistics (All Participants)")
        
        marks_per_q, total_marks_all = get_aggregate_stats(answers_path, correct_answers_map)
        
        st.write("**Total marks obtained by all participants per question:**")
        agg_table = [{"Question No.": q, "Total Marks": m} for q, m in marks_per_q.items()]
        st.table(agg_table)
        
        st.write(f"**Total marks obtained by all participants for the whole quiz: {total_marks_all}**")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            def restart_quiz():
                st.session_state.current_q = 0
                st.session_state.score = 0
                st.session_state.answers = {}
                get_aggregate_stats.clear()

            st.button("Restart Quiz", on_click=restart_quiz)
            
        with col2:
            if st.button("Quit"):
                st.session_state.quit = True
                st.rerun()

