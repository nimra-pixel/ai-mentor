# 🌟 AI Career Mentor

Tell it your dream career — it builds a personalised roadmap with phases, resources, milestones, timeline and salary info. Then ask it anything as a follow-up.

🚀 **[Live Demo →](https://your-app.streamlit.app)**

---

## What it does

1. You fill in: dream career, current level, education, skills, timeline, country
2. Groq llama-3.3-70b generates a structured JSON roadmap with 4-5 phases
3. Each phase has: skills, resources, milestones, daily commitment, tips
4. You get: salary info, job outlook, common mistakes, motivational message
5. Ask follow-up questions to your AI mentor after

## Features

- Fully personalised — different output for every profile
- Country-specific salary ranges and job market info
- Downloadable roadmap as markdown
- Follow-up Q&A chat with context from your roadmap
- Quick suggested questions built in

## Stack

`Python` `Streamlit` `Groq llama-3.3-70b` `JSON structured output` `requests`

## Run locally

```bash
git clone https://github.com/nimra-pixel/ai-mentor
cd ai-mentor
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

mkdir -p .streamlit
echo '[secrets]\nGROQ_API_KEY = "gsk_your_key_here"' > .streamlit/secrets.toml

streamlit run app.py
```

---

Built by [Nimra](https://linkedin.com/in/yourprofile) · AI Engineer Portfolio
