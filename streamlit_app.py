import streamlit as st
import requests
import os

# Try importing voice modules
try:
    import pyttsx3
    import speech_recognition as sr
    voice_enabled = True
    engine = pyttsx3.init()
except Exception:
    voice_enabled = False

# Set page config
st.set_page_config(page_title="Auto-GPT Mini", page_icon="🤖")
st.title("🤖 Simple Auto-GPT with Mistral + Voice + File Goals")

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# Function to speak text
def speak(text):
    if voice_enabled:
        engine.say(text)
        engine.runAndWait()

# Function to recognize voice
def listen_voice():
    if not voice_enabled:
        st.error("🎤 Voice input not supported in this environment.")
        return ""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening for your voice...")
        audio = recognizer.listen(source, timeout=5)
        try:
            text = recognizer.recognize_google(audio)
            st.success(f"🗣️ You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio.")
        except sr.RequestError as e:
            st.error(f"❌ Recognition error: {e}")
    return ""

# Read goals from file if exists
def read_goals_from_file():
    file_path = "goals.txt"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    return []

# Send a goal to Mistral via Ollama
def process_goal(goal):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": goal, "stream": False}
        )
        data = response.json()
        return data.get("response", "⚠️ No response from Mistral.")
    except Exception as e:
        return f"❌ Error: {e}"

# Interface controls
input_method = st.radio("Choose input method:", ["💬 Type", "🎤 Voice", "📄 From File"])

goal = ""

if input_method == "💬 Type":
    goal = st.text_input("🧠 What is your goal today?")

elif input_method == "🎤 Voice":
    if not voice_enabled:
        st.warning("🎤 Voice input is not available in this environment.")
    elif st.button("🎙️ Speak Now"):
        goal = listen_voice()

elif input_method == "📄 From File":
    goals = read_goals_from_file()
    if goals:
        goal = st.selectbox("📄 Choose a goal from file:", goals)
    else:
        st.warning("📁 No goals.txt file found or it's empty.")

# Process and respond
if goal:
    st.session_state.history.append({"role": "user", "content": goal})
    reply = process_goal(goal)
    st.session_state.history.append({"role": "assistant", "content": reply})

    st.success(f"🤖 Auto-GPT: {reply}")
    speak(reply)

# Display history
if st.session_state.history:
    st.markdown("## 🕓 Conversation History")
    for item in st.session_state.history:
        role = "🧠 You" if item["role"] == "user" else "🤖 Auto-GPT"
        st.markdown(f"**{role}:** {item['content']}")
