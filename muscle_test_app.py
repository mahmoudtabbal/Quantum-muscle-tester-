
import streamlit as st
import hashlib
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# Function to calculate SHA-256 score
def get_score(name, intention, item):
    seed = f"{name} + [{intention}] + {item}"
    hash_hex = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    score = int(hash_hex[:8], 16) % 100
    return score, hash_hex

# Interpretation scale
def interpret_score(score):
    if score <= 24:
        return "Weak – Detrimental"
    elif score <= 44:
        return "Weak – Incongruent"
    elif score <= 54:
        return "Neutral – No effect"
    elif score <= 74:
        return "Strong – Congruent/Neutral"
    elif score <= 89:
        return "Strong – Beneficial"
    else:
        return "Strong – Highly Beneficial"

# PDF generator
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Muscle Testing Report", ln=True, align="C")
    pdf.ln(10)
    for entry in data:
        for key, value in entry.items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
        pdf.ln(5)
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

# App layout
st.title("Intuitive Muscle Testing via SHA-256")

# Session state for name and results
if 'results' not in st.session_state:
    st.session_state.results = []
if 'name' not in st.session_state:
    st.session_state.name = ""

# Step 1: Get name
if not st.session_state.name:
    st.session_state.name = st.text_input("Enter your full name")
    st.stop()

# Step 2: Get intention and item
st.subheader(f"Welcome, {st.session_state.name}")
intention = st.text_input("What is your inquiry/intention?", placeholder="e.g., I want to feel energetic")
item = st.text_input("What item or idea do you want to test?", placeholder="e.g., labneh + egg + bread + olive oil")

if st.button("Generate Result"):
    if intention and item:
        score, hash_val = get_score(st.session_state.name, intention, item)
        interpretation = interpret_score(score)
        result = {
            "Name": st.session_state.name,
            "Intention": intention,
            "Item": item,
            "Score": score,
            "Interpretation": interpretation,
            "Hash": hash_val
        }
        st.session_state.results.append(result)
        st.success(f"Score: {score} - {interpretation}")
        st.code(f"Hash: {hash_val}")

# Show all results
if st.session_state.results:
    st.subheader("All Results")
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)

    # Excel download
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    st.download_button("Download as Excel", data=excel_buffer, file_name="muscle_test_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # PDF download
    pdf_buffer = create_pdf(st.session_state.results)
    st.download_button("Download as PDF", data=pdf_buffer, file_name="muscle_test_results.pdf", mime="application/pdf")
