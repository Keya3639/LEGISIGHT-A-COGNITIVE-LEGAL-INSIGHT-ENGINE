import streamlit as st 
import pandas as pd
import pickle
import joblib
import re
import psycopg2
import plotly.graph_objects as go
import spacy



def save_to_db(query, prediction, confidence):
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_queries (query_text, prediction, confidence)
            VALUES (%s, %s, %s)
        """, (query, int(prediction), float(confidence)))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.sidebar.error(f"Insert Error: {e}")
        return False

def generate_summary(text):
    text = text.lower()

    summaries = {

        "theft": (
            "This complaint involves a theft-related incident where property or valuable assets may have been unlawfully taken. "
            "Such cases are increasingly being reported and raise serious concerns about public safety and personal security. "
            "Theft not only results in financial loss but also creates psychological stress and fear among individuals. "
            "It reflects potential gaps in surveillance and preventive systems. "
            "Legal provisions under criminal law are applicable to ensure punishment and deterrence. "
            "Authorities must investigate evidence, identify suspects, and take necessary action. "
            "Overall, this case highlights the importance of maintaining law and order in society."
        ),

        "fraud": (
            "This complaint relates to a fraud case involving financial deception or misrepresentation. "
            "With the rise of digital platforms, such fraudulent activities are increasing rapidly. "
            "Victims often face financial loss and trust issues in systems and institutions. "
            "Fraud cases require detailed investigation and evidence collection for legal action. "
            "Existing laws provide strict punishment for such offenses. "
            "Preventive awareness and cybersecurity measures are essential in reducing such crimes. "
            "Overall, this case reflects a serious threat to financial stability and trust."
        ),

        "murder": (
            "This complaint concerns a severe criminal offense involving homicide or loss of life. "
            "Such cases are among the most serious and require immediate legal attention. "
            "They create fear and instability within society and deeply impact families. "
            "Thorough investigation, forensic analysis, and legal procedures are necessary. "
            "Strict punishments are applied under criminal law to ensure justice. "
            "Law enforcement must act swiftly to maintain order and prevent further harm. "
            "Overall, this case represents a critical threat to societal safety and justice."
        ),

        "assault": (
            "This complaint involves an assault case where physical harm or threat has occurred. "
            "Such incidents directly affect personal safety and public peace. "
            "Victims may suffer physical injuries as well as emotional trauma. "
            "Legal action is required to ensure accountability and prevent recurrence. "
            "Law enforcement plays a key role in controlling such crimes. "
            "Strict laws exist to punish offenders and protect victims. "
            "Overall, this case highlights the importance of maintaining safety and discipline in society."
        ),

        "cybercrime": (
            "This complaint relates to cybercrime involving digital fraud, hacking, or data theft. "
            "With increasing internet usage, such crimes are rising rapidly. "
            "Cybercrime can lead to financial loss and compromise of sensitive data. "
            "Identifying perpetrators is often challenging due to digital anonymity. "
            "Legal frameworks exist to tackle such crimes, but enforcement is complex. "
            "Awareness and cybersecurity measures are crucial in prevention. "
            "Overall, this case highlights the growing importance of digital security."
        ),

        "abuse": (
            "This complaint highlights potential abuse or mistreatment of an individual. "
            "Such cases may involve physical, emotional, or psychological harm. "
            "Victims often face long-term trauma and require support and protection. "
            "Legal systems provide mechanisms to address and prevent abuse. "
            "Timely reporting and intervention are crucial for justice. "
            "Authorities must ensure victim safety and strict action against offenders. "
            "Overall, this case emphasizes the importance of protecting human rights."
        ),

        "domestic violence": (
            "This complaint involves domestic violence occurring within a household environment. "
            "Such cases often remain underreported due to fear and social stigma. "
            "Victims may suffer continuous physical and emotional harm. "
            "Legal provisions exist to protect victims and take strict action. "
            "Support systems and awareness play a crucial role in addressing such issues. "
            "Immediate intervention is necessary to prevent further harm. "
            "Overall, this case reflects a serious issue affecting family and social stability."
        ),

        "property dispute": (
            "This complaint relates to a dispute over ownership or usage of property. "
            "Such conflicts often arise between family members or business parties. "
            "They may involve legal documentation and ownership verification. "
            "Property disputes can lead to long legal battles and financial stress. "
            "Legal frameworks are available to resolve such disputes fairly. "
            "Proper documentation and legal procedures are essential. "
            "Overall, this case highlights the importance of clear property rights."
        ),

        "contract": (
            "This complaint involves a contract-related dispute between involved parties. "
            "Such cases arise when agreements are not honored or misinterpreted. "
            "They may involve financial transactions or service agreements. "
            "Legal enforcement ensures fairness and accountability. "
            "Courts analyze contract terms and obligations carefully. "
            "Proper documentation is crucial in resolving such disputes. "
            "Overall, this case emphasizes the importance of clear contractual agreements."
        ),

        "harassment": (
            "This complaint involves harassment or repeated unwanted behavior. "
            "Such actions can cause emotional distress and discomfort to victims. "
            "Harassment may occur in workplaces, public spaces, or online platforms. "
            "Legal systems provide protection and remedies against such behavior. "
            "Victims are encouraged to report incidents promptly. "
            "Strict laws help in controlling and preventing harassment. "
            "Overall, this case highlights the importance of respectful social interaction."
        ),

        "corruption": (
            "This complaint relates to corruption involving misuse of power or authority. "
            "Corruption undermines fairness, justice, and institutional integrity. "
            "It can impact governance and public trust significantly. "
            "Legal frameworks exist to detect and punish corrupt practices. "
            "Transparency and accountability are key in preventing corruption. "
            "Authorities must ensure strict monitoring and enforcement. "
            "Overall, this case reflects a major issue affecting societal development."
        )
    }

    for key in summaries:
        if key in text:
            return summaries[key]

    return (
        "This complaint describes a legal issue requiring detailed examination and resolution. "
        "Such matters may involve disputes, violations, or conflicts affecting individuals or organizations. "
        "Understanding the nature of the issue is essential for determining legal action. "
        "Investigation and evidence collection may be required. "
        "Legal authorities ensure fairness and proper judgment. "
        "Timely resolution helps maintain justice and order. "
        "Overall, this case highlights the importance of an effective legal system."
    )


def clean_text(text):
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9., ]', '', text)
    return text.lower()

df["clean_text"] = df["full_text"].apply(clean_text)
df = df.dropna(subset=["clean_text"])
df = df[df["clean_text"].str.strip() != ""]
df = df.reset_index(drop=True)

def detect_case_type(text):
    text = text.lower()

    if "domestic violence" in text:
        return "domestic violence"
    elif "property dispute" in text:
        return "property"
    elif "contract" in text:
        return "contract"
    elif "cyber" in text:
        return "cybercrime"
    elif "fraud" in text:
        return "fraud"
    elif "theft" in text:
        return "theft"
    elif "murder" in text:
        return "murder"
    elif "assault" in text:
        return "assault"
    elif "harassment" in text:
        return "harassment"
    elif "corruption" in text:
        return "corruption"
    elif "abuse" in text:
        return "abuse"

    return "general"

def calculate_deadline(case_type):
    today = datetime.today()

    rules = {
        "theft": 30,
        "fraud": 45,
        "murder": 60,
        "assault": 30,
        "cybercrime": 20,
        "abuse": 25,
        "domestic violence": 15,
        "property": 90,
        "contract": 60,
        "harassment": 20,
        "corruption": 60,
        "general": 30
    }
    days = rules.get(case_type, 30)
    if remaining <= 5:
        status = "⚠️ Due Soon"
    elif remaining <= 0:
        status = "❌ Overdue"
    else:
        status = "✅ On Track"

    return deadline.strftime("%d-%m-%Y"), remaining, status

def extract_entities(text):
    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))

    return entities

# LOAD MODEL
with open("../models/tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

model = joblib.load("../models/escalation_model.pkl")


st.set_page_config(page_title="LegiSight", layout="wide")

st.title("⚖️ LegiSight - Cognitive Legal Insight Engine")
st.markdown("AI-powered legal complaint intelligence system")



search_clicked = st.button("🔍 Search")

if search_clicked and query:

    cleaned_query = clean_text(query)
    query_vector = vectorizer.transform([cleaned_query])

    ml_prediction = model.predict(query_vector)[0]
    rule_prediction = rule_based_priority(query)

    prediction = rule_prediction if rule_prediction is not None else ml_prediction

    probs = model.predict_proba(query_vector)[0]
    probability = float(max(probs))

    if probability > 0.95:
        probability = 0.85 + (probability - 0.95)

    summary = generate_summary(query)

    saved = save_to_db(query, prediction, probability)

    st.subheader("👩‍💻 Complaint Summary")
    st.info(summary)

    st.subheader("📝 Named Entities & Legal Insights")

    entities = extract_entities(query)

    legal_keywords = [
        "theft", "fraud", "murder", "assault",
        "cybercrime", "abuse", "harassment",
        "property", "contract", "corruption"
    ]

    found_keywords = [k for k in legal_keywords if k in query.lower()]

    if entities:
        st.markdown("**🔍 Detected Entities:**")
        for ent, label in entities:
            st.write(f"🔹 {ent} ({label})")

    if found_keywords:
        st.markdown("**⚖️ Legal Keywords Detected:**")
        for k in found_keywords:
            st.write(f"⚖️ {k.title()} Case")

    if not entities and not found_keywords:
        st.write("No significant entities found.")

    case_type = detect_case_type(query)
    deadline, remaining, status = calculate_deadline(case_type)

    st.subheader("📅 Legal Deadline")

    col1, col2, col3 = st.columns(3)
    col1.metric("Deadline Date", deadline)
    col2.metric("Days Remaining", remaining)
    col3.metric("Status", status)

    st.subheader("🔍 Prediction Result")

    if prediction == 1:
        st.error("⚠️ High Escalation Risk")
    else:
        st.success("✅ Low Escalation Risk")

    st.metric("Confidence Score", f"{round(probability*100,2)}%")
    st.progress(probability)

    st.subheader("🎯 Confidence Gauge")

    confidence_percent = probability * 100

if confidence_percent < 50:
    level = "🔴 Low Confidence"
elif confidence_percent < 75:
    level = "🟡 Medium Confidence"
else:
    level = "🟢 High Confidence"

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=confidence_percent,
    title={'text': "Prediction Confidence"},
    
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "black"},
        
        'steps': [
            {'range': [0, 50], 'color': "red"},
            {'range': [50, 75], 'color': "yellow"},
            {'range': [75, 100], 'color': "green"}
        ],
        
        'threshold': {
            'line': {'color': "blue", 'width': 4},
            'thickness': 0.75,
            'value': confidence_percent
        }
    }
))

fig.update_layout(height=300)

st.plotly_chart(fig)

st.markdown(f"### {level}")

st.markdown("""
**Confidence Levels:**
- 🔴 0–50 → Low Confidence  
- 🟡 50–75 → Medium Confidence  
- 🟢 75–100 → High Confidence  
""")

    #  SIMILAR CASES 

st.subheader("📚 Similar Cases")
st.caption("Top 5 most relevant legal cases")

from sklearn.metrics.pairwise import cosine_similarity

embeddings = vectorizer.transform(df["clean_text"])
scores = cosine_similarity(query_vector, embeddings)[0]

results = list(enumerate(scores))

results = sorted(results, key=lambda x: x[1], reverse=True)

shown = 0

for idx, score in results:
    row = df.iloc[idx]
    text = str(row["clean_text"]).strip()

    if len(text) < 100:
        continue

    if any(bad in text for bad in ["in my view", "supra", "herein", "thereof"]):
        continue

    title = get_case_title(row)

    if title is None:
        continue

    # 🎯 Display
    st.markdown(f"### 🕵️‍♀️ {title}")
    st.write(text[:250] + "...")
    st.write("---")

    shown += 1
    if shown == 5:
        break

#  METRIC CARDS
st.markdown("### 📌 Overview")

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div style="background-color:#f0f2f6;padding:20px;border-radius:10px;text-align:center">
<h3>📁 Total Cases</h3>
<h2>{len(df)}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style="background-color:#ffe6e6;padding:20px;border-radius:10px;text-align:center">
<h3>⚠️ High Risk</h3>
<h2>{high_risk}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style="background-color:#e6ffe6;padding:20px;border-radius:10px;text-align:center">
<h3>✅ Low Risk</h3>
<h2>{low_risk}</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("### 💡 Insights")

col4, col5 = st.columns(2)

with col4:
    fig1 = px.histogram(df, x="year", title="📈 Cases Over Time", color_discrete_sequence=["#6A5ACD"])  
    fig1.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    st.plotly_chart(fig1, use_container_width=True)
    
with col5:
    cat_counts = df["category"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]

    fig2 = px.pie(cat_counts, names="Category", values="Count", title="📂 Case Categories",color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig2, use_container_width=True)

#  RISK BAR
st.markdown("### ⚠️ Risk Analysis")

risk_df = pd.DataFrame({
    "Risk": ["High Risk", "Low Risk"],
    "Count": [high_risk, low_risk]
})

fig3 = px.bar(
    risk_df,
    x="Risk",
    y="Count",
    title="Risk Distribution",
    color="Risk",
    color_discrete_map={
        "High Risk":"#8A2BE2"  ,
        "Low Risk":   "#000080"
    }
)

fig3.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.markdown("Developed by **Keya Das** | LegiSight: A Cognitive Legal Insight Engine")
