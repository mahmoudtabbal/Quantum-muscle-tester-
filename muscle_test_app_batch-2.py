
import streamlit as st
import hashlib
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# Function to calculate SHA-256 score
def get_score(name, intention, item, timing=""):
    seed = f"{name} + [{intention}] + {item}"
    if timing:
        seed += f" + {timing}"
    hash_hex = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    score = int(hash_hex[:8], 16) % 100
    return score

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
        for key in ["Name", "Intention", "Item", "Timing", "Score", "Interpretation"]:
            value = entry.get(key, "")
            text = f"{key}: {value}"
            safe_text = text.encode('latin1', 'replace').decode('latin1')
            pdf.cell(200, 10, txt=safe_text, ln=True)
        pdf.ln(5)
    pdf_output = pdf.output(dest='S').encode('latin1', 'replace')
    return BytesIO(pdf_output)

# App layout
st.title("Batch Muscle Testing via SHA-256")

if 'results' not in st.session_state:
    st.session_state.results = []
if 'name' not in st.session_state:
    st.session_state.name = ""

if not st.session_state.name:
    st.session_state.name = st.text_input("Enter your full name")
    st.stop()

st.subheader(f"Welcome, {st.session_state.name}")

intention = st.text_input("What is your inquiry/intention?")
timing_note = st.text_input("Optional: Timing note (e.g., at breakfast, spring, full moon)")

uploaded_file = st.file_uploader("Upload CSV file with a list of items to test", type=["csv"])

if uploaded_file and intention:
    df_items = pd.read_csv(uploaded_file)
    if 'Item' not in df_items.columns:
        st.error("CSV must have a column named 'Item'")
    else:
        for _, row in df_items.iterrows():
            item = row['Item']
            score = get_score(st.session_state.name, intention, item, timing_note)
            interpretation = interpret_score(score)
            result = {
                "Name": st.session_state.name,
                "Intention": intention,
                "Item": item,
                "Timing": timing_note,
                "Score": score,
                "Interpretation": interpretation
            }
            st.session_state.results.append(result)
        st.success("Batch testing completed.")

if st.session_state.results:
    st.subheader("Results")
    df_results = pd.DataFrame(st.session_state.results)
    st.dataframe(df_results)

    # Excel
    excel_buffer = BytesIO()
    df_results.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    st.download_button("Download Excel", data=excel_buffer, file_name="muscle_test_batch_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # PDF
    pdf_buffer = create_pdf(st.session_state.results)
    st.download_button("Download PDF", data=pdf_buffer, file_name="muscle_test_batch_results.pdf", mime="application/pdf")
