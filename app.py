import streamlit as st
import requests
import json
import re
import time

st.set_page_config(
    page_title="AI Career Mentor",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.hero {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 20px; padding: 3rem 2rem 2.5rem;
    margin-bottom: 1.5rem; text-align: center;
    border: 1px solid #3d3580;
}
.hero h1 { font-size: 2.2rem; font-weight: 700; color: #f0f6fc; margin: 0; }
.hero p  { color: #a0aec0; margin: .5rem 0 0; font-size: 1rem; }
.hero .badge {
    display: inline-block; background: rgba(159,122,234,0.15);
    color: #d6bcfa; font-size: .75rem; font-weight: 600;
    padding: 5px 14px; border-radius: 20px;
    border: 1px solid #9f7aea; margin-top: .8rem;
}

.phase-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 1.2rem 1.4rem;
    margin-bottom: 1rem; position: relative;
    overflow: hidden;
}
.phase-card::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0;
    width: 4px; border-radius: 4px 0 0 4px;
}
.phase-1::before { background: #f6ad55; }
.phase-2::before { background: #68d391; }
.phase-3::before { background: #63b3ed; }
.phase-4::before { background: #b794f4; }
.phase-5::before { background: #fc8181; }

.phase-header {
    display: flex; align-items: center; gap: 10px; margin-bottom: .8rem;
}
.phase-num {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: .8rem; font-weight: 700; flex-shrink: 0;
}
.phase-title { font-size: 1rem; font-weight: 600; color: #f0f6fc; }
.phase-time  { font-size: .75rem; color: #8b949e; margin-left: auto;
               background: #21262d; padding: 3px 10px; border-radius: 20px; }
.phase-body  { font-size: .88rem; color: #c9d1d9; line-height: 1.7; margin-left: 42px; }

.resource-chip {
    display: inline-block; background: #1c2d3f; color: #79c0ff;
    font-size: .73rem; padding: 3px 10px; border-radius: 20px;
    border: 1px solid #2d4a6e; margin: 3px;
}
.skill-chip {
    display: inline-block; background: #1f3a2f; color: #3fb950;
    font-size: .73rem; padding: 3px 10px; border-radius: 20px;
    border: 1px solid #2d5a3f; margin: 3px;
}
.milestone-chip {
    display: inline-block; background: #2d1a3f; color: #d6bcfa;
    font-size: .73rem; padding: 3px 10px; border-radius: 20px;
    border: 1px solid #5a3a8a; margin: 3px;
}
.summary-card {
    background: linear-gradient(135deg, #1a1033, #0d1f2d);
    border: 1px solid #3d3580; border-radius: 12px;
    padding: 1.4rem 1.6rem; margin-bottom: 1.2rem;
}
.summary-card h3 { color: #d6bcfa; font-size: 1.1rem; margin: 0 0 .5rem; }
.summary-card p  { color: #a0aec0; font-size: .9rem; line-height: 1.7; margin: 0; }
.stat-row { display: flex; gap: 10px; margin-bottom: 1rem; flex-wrap: wrap; }
.stat-card {
    flex: 1; min-width: 100px; background: #161b22;
    border: 1px solid #30363d; border-radius: 10px;
    padding: .8rem; text-align: center;
}
.stat-card .val { font-size: 1.3rem; font-weight: 700; color: #d6bcfa; }
.stat-card .lbl { font-size: .72rem; color: #8b949e; margin-top: 2px; }
.warning-box {
    background: #2d1f0d; border: 1px solid #f0883e;
    border-radius: 8px; padding: .8rem 1rem;
    font-size: .82rem; color: #f0883e; margin-bottom: .8rem;
}
</style>
""", unsafe_allow_html=True)

# ── Groq API ──────────────────────────────────────────────────────────────────
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL    = "llama-3.3-70b-versatile"

def get_key():
    k = st.secrets.get("GROQ_API_KEY", "")
    if not k:
        st.error("⚠️ GROQ_API_KEY not found in Streamlit secrets.")
        st.stop()
    return k

def groq_call(messages, max_tokens=3000):
    r = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {get_key()}",
                 "Content-Type": "application/json"},
        json={"model": MODEL, "messages": messages,
              "temperature": 0.5, "max_tokens": max_tokens},
        timeout=45,
    )
    if r.status_code != 200:
        st.error(f"Groq error: {r.json().get('error',{}).get('message','Unknown')}")
        st.stop()
    return r.json()["choices"][0]["message"]["content"].strip()

# ── Roadmap generator ─────────────────────────────────────────────────────────
def generate_roadmap(career, current_level, education, skills,
                     timeline, learning_style, country):
    prompt = f"""You are an expert career mentor and educator. Generate a detailed, personalised career roadmap.

Student profile:
- Dream career: {career}
- Current level: {current_level}
- Education background: {education}
- Current skills: {skills if skills else 'Not specified'}
- Timeline goal: {timeline}
- Preferred learning style: {learning_style}
- Country/Region: {country}

Generate a JSON response with this EXACT structure (no markdown, no explanation, pure JSON):
{{
  "career_title": "exact career title",
  "summary": "2-3 sentence personalised overview of their journey",
  "total_duration": "e.g. 18 months",
  "difficulty": "Beginner/Intermediate/Advanced",
  "job_outlook": "brief sentence on job market",
  "avg_salary": "salary range for {country}",
  "phases": [
    {{
      "phase": 1,
      "title": "Phase title",
      "duration": "e.g. 0-3 months",
      "goal": "What they achieve in this phase",
      "skills": ["skill1", "skill2", "skill3"],
      "resources": ["Resource name 1", "Resource name 2", "Resource name 3"],
      "milestones": ["Milestone 1", "Milestone 2"],
      "daily_commitment": "e.g. 2 hours/day",
      "tips": "One practical tip for this phase"
    }}
  ],
  "top_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "common_mistakes": ["mistake1", "mistake2", "mistake3"],
  "motivational_message": "A short personalised motivational closing message"
}}

Generate 4-5 phases. Make it highly specific and actionable for someone in {country} pursuing {career}."""

    response = groq_call([
        {"role": "system", "content":
         "You are an expert career mentor. Always respond with valid JSON only. "
         "No markdown, no code blocks, no explanation. Pure JSON."},
        {"role": "user", "content": prompt}
    ], max_tokens=3000)

    # Clean and parse JSON
    clean = re.sub(r"```json|```", "", response).strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Try to extract JSON object
        match = re.search(r'\{.*\}', clean, re.DOTALL)
        if match:
            return json.loads(match.group())
        st.error("Could not parse roadmap. Please try again.")
        st.stop()

def generate_followup(question, roadmap_context, career):
    return groq_call([
        {"role": "system", "content":
         f"You are an expert career mentor for someone pursuing {career}. "
         "Answer questions based on their personalised roadmap. Be concise and practical."},
        {"role": "user", "content":
         f"Roadmap context: {roadmap_context}\n\nQuestion: {question}"}
    ], max_tokens=500)

# ── Phase colours ─────────────────────────────────────────────────────────────
PHASE_COLORS = [
    ("#f6ad55", "#2d2010"),  # orange
    ("#68d391", "#1a2d1f"),  # green
    ("#63b3ed", "#1a2535"),  # blue
    ("#b794f4", "#2d1a3f"),  # purple
    ("#fc8181", "#2d1a1a"),  # red
]
PHASE_CLASSES = ["phase-1", "phase-2", "phase-3", "phase-4", "phase-5"]

# ── Session state ─────────────────────────────────────────────────────────────
if "roadmap"   not in st.session_state: st.session_state.roadmap = None
if "qa_history" not in st.session_state: st.session_state.qa_history = []
if "profile"   not in st.session_state: st.session_state.profile = {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌟 Your Profile")

    career = st.text_input("Dream career / job title",
        placeholder="e.g. AI Engineer, Data Scientist, UX Designer")

    current_level = st.selectbox("Current level", [
        "Complete beginner", "Some self-study done",
        "Student (university)", "Fresh graduate",
        "Working professional (career change)",
        "Experienced — want to specialise"
    ])

    education = st.text_input("Your education background",
        placeholder="e.g. BSc Computer Science, MBA, High school grad")

    skills = st.text_area("Skills you already have (optional)",
        placeholder="e.g. Python basics, Excel, teaching experience",
        height=80)

    timeline = st.selectbox("Your goal timeline", [
        "As fast as possible (6 months)",
        "1 year",
        "1.5 years",
        "2 years",
        "No rush — learn properly (2+ years)",
    ])

    learning_style = st.selectbox("Preferred learning style", [
        "Videos & courses (YouTube, Coursera)",
        "Books & reading",
        "Hands-on projects",
        "Bootcamp / structured program",
        "Mix of everything",
    ])

    country = st.text_input("Your country / region",
        placeholder="e.g. Pakistan, UK, USA, India")

    st.markdown("---")
    generate = st.button("🚀 Generate My Roadmap", type="primary",
                          use_container_width=True,
                          disabled=not (career and country))

    if not career or not country:
        st.caption("Fill in career and country to generate.")

    if st.session_state.roadmap:
        if st.button("🔄 Start over", use_container_width=True):
            st.session_state.roadmap = None
            st.session_state.qa_history = []
            st.session_state.profile = {}
            st.rerun()

    st.markdown("---")
    st.markdown("""**Stack**  
    Groq llama-3.3-70b  
    Streamlit · Python · requests  
    JSON structured output
    """)
    st.caption("Built by Nimra · [GitHub](https://github.com/nimra-pixel)")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🌟 AI Career Mentor</h1>
  <p>Share your dream career — get a personalised roadmap with phases, resources, milestones and timeline</p>
  <span class="badge">⚡ Powered by Groq llama-3.3-70b · Personalised for YOU</span>
</div>
""", unsafe_allow_html=True)

# ── Landing state ─────────────────────────────────────────────────────────────
if not st.session_state.roadmap and not generate:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style='background:#161b22;border:1px solid #30363d;border-radius:12px;padding:1.2rem;text-align:center'>
        <div style='font-size:2rem'>🎯</div>
        <div style='color:#f0f6fc;font-weight:600;margin:.5rem 0'>Personalised phases</div>
        <div style='color:#8b949e;font-size:.85rem'>4-5 phases tailored to your current level and timeline</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style='background:#161b22;border:1px solid #30363d;border-radius:12px;padding:1.2rem;text-align:center'>
        <div style='font-size:2rem'>📚</div>
        <div style='color:#f0f6fc;font-weight:600;margin:.5rem 0'>Curated resources</div>
        <div style='color:#8b949e;font-size:.85rem'>Specific courses, books, and tools for each phase</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style='background:#161b22;border:1px solid #30363d;border-radius:12px;padding:1.2rem;text-align:center'>
        <div style='font-size:2rem'>💬</div>
        <div style='color:#f0f6fc;font-weight:600;margin:.5rem 0'>Ask follow-up questions</div>
        <div style='color:#8b949e;font-size:.85rem'>Chat with your mentor after getting the roadmap</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💡 Example careers people are exploring")
    examples = [
        ("🤖", "AI Engineer", "Pakistan"),
        ("📊", "Data Scientist", "UK"),
        ("🎨", "UX Designer", "India"),
        ("☁️", "Cloud Architect", "USA"),
        ("🔒", "Cybersecurity Analyst", "Pakistan"),
        ("📱", "Mobile App Developer", "Canada"),
    ]
    cols = st.columns(3)
    for i, (icon, c, ctry) in enumerate(examples):
        with cols[i % 3]:
            if st.button(f"{icon} {c}", key=f"ex_{i}", use_container_width=True):
                st.session_state["_career"] = c
                st.session_state["_country"] = ctry
    st.stop()

# ── Generate roadmap ──────────────────────────────────────────────────────────
if generate and career and country:
    with st.spinner("🧠 Building your personalised roadmap..."):
        t0 = time.time()
        roadmap = generate_roadmap(
            career, current_level, education,
            skills, timeline, learning_style, country
        )
        st.session_state.roadmap = roadmap
        st.session_state.profile = {
            "career": career, "level": current_level,
            "country": country, "timeline": timeline,
        }
        st.success(f"✅ Roadmap generated in {round(time.time()-t0, 1)}s")

# ── Display roadmap ───────────────────────────────────────────────────────────
if st.session_state.roadmap:
    rm = st.session_state.roadmap

    # Summary card
    st.markdown(f"""
    <div class="summary-card">
      <h3>🎯 Your path to becoming a {rm.get('career_title', career)}</h3>
      <p>{rm.get('summary', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card"><div class="val">{rm.get('total_duration','—')}</div><div class="lbl">Total duration</div></div>
      <div class="stat-card"><div class="val">{len(rm.get('phases', []))}</div><div class="lbl">Phases</div></div>
      <div class="stat-card"><div class="val">{rm.get('difficulty','—')}</div><div class="lbl">Difficulty</div></div>
      <div class="stat-card"><div class="val">{rm.get('avg_salary','—')}</div><div class="lbl">Avg salary</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Job outlook
    if rm.get("job_outlook"):
        st.markdown(f"""
        <div style='background:#1a2535;border:1px solid #2d4a6e;border-radius:8px;
                    padding:.7rem 1rem;font-size:.85rem;color:#79c0ff;margin-bottom:1rem'>
        📈 <strong>Job outlook:</strong> {rm['job_outlook']}
        </div>""", unsafe_allow_html=True)

    # Phases
    st.markdown("## 🗺️ Your Learning Roadmap")
    for i, phase in enumerate(rm.get("phases", [])):
        color, bg = PHASE_COLORS[i % len(PHASE_COLORS)]
        pc = PHASE_CLASSES[i % len(PHASE_CLASSES)]

        with st.expander(
            f"Phase {phase.get('phase', i+1)}: {phase.get('title','—')}  ·  {phase.get('duration','—')}",
            expanded=(i == 0)
        ):
            st.markdown(f"**🎯 Goal:** {phase.get('goal','')}")
            st.markdown(f"**⏰ Daily commitment:** {phase.get('daily_commitment','')}")
            st.markdown(f"**💡 Tip:** *{phase.get('tips','')}*")

            if phase.get("skills"):
                st.markdown("**🛠️ Skills to learn:**")
                chips = "".join(f"<span class='skill-chip'>{s}</span>"
                                for s in phase["skills"])
                st.markdown(chips, unsafe_allow_html=True)

            if phase.get("resources"):
                st.markdown("**📚 Resources:**")
                chips = "".join(f"<span class='resource-chip'>📖 {r}</span>"
                                for r in phase["resources"])
                st.markdown(chips, unsafe_allow_html=True)

            if phase.get("milestones"):
                st.markdown("**🏆 Milestones:**")
                chips = "".join(f"<span class='milestone-chip'>✓ {m}</span>"
                                for m in phase["milestones"])
                st.markdown(chips, unsafe_allow_html=True)

    # Top skills
    if rm.get("top_skills"):
        st.markdown("## 🛠️ Top skills you'll need")
        chips = "".join(f"<span class='skill-chip'>{s}</span>"
                        for s in rm["top_skills"])
        st.markdown(chips, unsafe_allow_html=True)

    # Common mistakes
    if rm.get("common_mistakes"):
        st.markdown("## ⚠️ Common mistakes to avoid")
        for m in rm["common_mistakes"]:
            st.markdown(f'<div class="warning-box">⚠️ {m}</div>',
                        unsafe_allow_html=True)

    # Motivational message
    if rm.get("motivational_message"):
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1a1033,#0d1f2d);
                    border:1px solid #3d3580;border-radius:12px;
                    padding:1.4rem 1.6rem;margin:1rem 0;text-align:center'>
          <div style='font-size:1.5rem;margin-bottom:.5rem'>💪</div>
          <div style='color:#d6bcfa;font-size:.95rem;line-height:1.7;font-style:italic'>
            "{rm['motivational_message']}"
          </div>
        </div>""", unsafe_allow_html=True)

    # Download
    roadmap_md = f"# Career Roadmap: {rm.get('career_title', career)}\n\n"
    roadmap_md += f"**Summary:** {rm.get('summary','')}\n\n"
    roadmap_md += f"**Duration:** {rm.get('total_duration','')} | **Salary:** {rm.get('avg_salary','')}\n\n"
    for phase in rm.get("phases", []):
        roadmap_md += f"## Phase {phase.get('phase')}: {phase.get('title')} ({phase.get('duration')})\n"
        roadmap_md += f"**Goal:** {phase.get('goal')}\n\n"
        roadmap_md += f"**Skills:** {', '.join(phase.get('skills',[]))}\n\n"
        roadmap_md += f"**Resources:** {', '.join(phase.get('resources',[]))}\n\n"
        roadmap_md += f"**Milestones:** {', '.join(phase.get('milestones',[]))}\n\n"

    st.download_button(
        "⬇️ Download roadmap (.md)",
        data=roadmap_md,
        file_name=f"roadmap_{career.replace(' ','_')}.md",
        mime="text/markdown",
    )

    # ── Q&A follow-up ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 💬 Ask your AI mentor anything")
    st.caption("Have a question about your roadmap? Ask for more detail, alternatives, or advice.")

    # Show history
    for qa in st.session_state.qa_history:
        st.markdown(f"""
        <div style='background:#1c2333;border:1px solid #30363d;border-radius:8px;
                    padding:.7rem 1rem;margin:.4rem 0;font-size:.88rem;color:#f0f6fc'>
        🙋 <strong>You:</strong> {qa['q']}
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:#161b22;border:1px solid #30363d;
                    border-left:3px solid #9f7aea;border-radius:8px;
                    padding:.7rem 1rem;margin:.4rem 0;font-size:.88rem;color:#f0f6fc'>
        🌟 <strong>Mentor:</strong> {qa['a']}
        </div>""", unsafe_allow_html=True)

    # Suggested questions
    suggested = [
        "How do I stay motivated during this journey?",
        "What if I can only study 1 hour a day?",
        "Which phase is the hardest?",
        "How do I get my first job/internship?",
        "What should I build for my portfolio?",
    ]
    st.markdown("**Quick questions:**")
    cols = st.columns(len(suggested))
    for i, (col, q) in enumerate(zip(cols, suggested)):
        with col:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                st.session_state["_followup"] = q
                st.rerun()

    question = st.chat_input("Ask your mentor...")
    if "_followup" in st.session_state:
        question = st.session_state.pop("_followup")

    if question:
        with st.spinner("🌟 Your mentor is thinking..."):
            context = json.dumps({
                "career": rm.get("career_title"),
                "phases": [{"title": p["title"], "duration": p["duration"]}
                           for p in rm.get("phases", [])],
                "total_duration": rm.get("total_duration"),
                "profile": st.session_state.profile,
            })
            answer = generate_followup(question, context,
                                       rm.get("career_title", career))

        st.session_state.qa_history.append({"q": question, "a": answer})
        st.rerun()
