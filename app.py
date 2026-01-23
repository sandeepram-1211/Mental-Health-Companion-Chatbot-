"""Mental Health Companion Chatbot - All in One"""
import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime
from textblob import TextBlob

# Try to load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# ============================================================================
# API Handler for Groq (FREE & Fast)
# ============================================================================
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class APIHandler:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.enabled = False
        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                self.enabled = True
            except:
                pass
    
    def is_available(self):
        return self.enabled
    
    def generate_response(self, user_input, sentiment_result, conversation_history=None):
        if not self.enabled:
            return None
        
        try:
            system_prompt = """You are a compassionate mental health companion. Provide empathetic, supportive responses (2-3 sentences). Be warm and understanding."""
            
            sentiment = sentiment_result.get('sentiment', 'neutral')
            user_message = f"User mood: {sentiment}\n\nUser says: {user_input}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if conversation_history:
                for msg in conversation_history[-4:]:
                    role = "user" if msg.get('role') == 'user' else "assistant"
                    if msg.get('content'):
                        messages.append({"role": role, "content": msg['content']})
            
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
    
    def set_api_key(self, api_key):
        self.api_key = api_key
        if api_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=api_key)
                self.enabled = True
            except:
                self.enabled = False
        else:
            self.enabled = False

# ============================================================================
# Sentiment Analyzer
# ============================================================================
class SentimentAnalyzer:
    def analyze(self, text):
        if not text or not text.strip():
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        try:
            blob = TextBlob(text)
            score = blob.sentiment.polarity
            
            if score > 0.1:
                sentiment = 'positive'
            elif score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': round(score, 3),
                'confidence': abs(score)
            }
        except:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}

# ============================================================================
# Relaxation Tips
# ============================================================================
class RelaxationTips:
    def __init__(self):
        self.tips = [
            "Take 5 deep breaths: Inhale 4 counts, hold 4, exhale 4. Repeat.",
            "Go for a short walk outside. Fresh air helps clear your mind.",
            "Listen to calming music or nature sounds.",
            "Write down your thoughts in a journal.",
            "Do a 5-minute meditation focusing on your breath.",
            "Drink a warm cup of tea and take a moment to relax.",
            "Stretch your body gently to release tension.",
            "Practice gratitude: Write 3 things you're grateful for.",
            "Take a break from screens for 10 minutes.",
            "Do something creative: draw, color, or write.",
            "Practice the 5-4-3-2-1 technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste."
        ]
    
    def get_random_tip(self):
        return random.choice(self.tips)

# ============================================================================
# Mental Health Chatbot
# ============================================================================
class MentalHealthChatbot:
    def __init__(self):
        self.api_handler = APIHandler()
        self.crisis_keywords = ['suicide', 'kill myself', 'end my life', 'hurt myself', 'want to die']
        
    def _get_crisis_response(self):
        return """I'm concerned about your safety. Please contact:
- Emergency: 911 (US) or 112 (EU)
- Crisis Text Line: Text HOME to 741741
- Suicide Prevention: 988 (US)

This chatbot cannot replace professional help. Please reach out to someone you trust or a mental health professional immediately."""
    
    def _check_crisis(self, text):
        return any(word in text.lower() for word in self.crisis_keywords)
    
    def _get_local_response(self, sentiment, user_input):
        responses = {
            'positive': "I'm glad you're feeling positive! Keep nurturing these good feelings.",
            'neutral': "I hear you. How are you feeling about things right now?",
            'negative': "I'm sorry you're going through this. Your feelings are valid. Would you like to talk more about what's bothering you?"
        }
        base = responses.get(sentiment, responses['neutral'])
        
        if any(w in user_input.lower() for w in ['anxious', 'worried']):
            base += " Anxiety can be overwhelming. Would you like to try some breathing exercises?"
        elif any(w in user_input.lower() for w in ['sad', 'depressed']):
            base += " Remember that these feelings can change. You're not alone."
        elif any(w in user_input.lower() for w in ['stressed', 'overwhelmed']):
            base += " Stress can feel overwhelming. Breaking things into smaller steps can help."
        
        return base
    
    def get_response(self, user_input, sentiment_result, conversation_history=None):
        if self._check_crisis(user_input):
            return self._get_crisis_response()
        
        if self.api_handler.is_available():
            api_response = self.api_handler.generate_response(user_input, sentiment_result, conversation_history)
            if api_response:
                return api_response
        
        sentiment = sentiment_result.get('sentiment', 'neutral')
        return self._get_local_response(sentiment, user_input)
    
    def is_api_enabled(self):
        return self.api_handler.is_available()
    
    def set_api_key(self, api_key):
        self.api_handler.set_api_key(api_key)

# ============================================================================
# Streamlit App
# ============================================================================
st.set_page_config(page_title="Mental Health Companion", page_icon="💚", layout="wide")

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = MentalHealthChatbot()
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = SentimentAnalyzer()
if 'tips' not in st.session_state:
    st.session_state.tips = RelaxationTips()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'mood_history' not in st.session_state:
    st.session_state.mood_history = []

# Header
st.title("💚 Mental Health Companion Chatbot")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.info("🆓 **FREE API**: Get key at https://console.groq.com/keys")
    api_key = st.text_input("Groq API Key (Optional)", type="password", 
                           value=os.getenv('GROQ_API_KEY', ''))
    
    if api_key:
        st.session_state.chatbot.set_api_key(api_key)
    
    if st.session_state.chatbot.is_api_enabled():
        st.success("🤖 AI Mode: Enabled")
    else:
        st.info("💬 Standard Mode: Local responses")
    
    st.markdown("---")
    
    st.header("📊 Mood Tracker")
    if st.session_state.mood_history:
        try:
            df = pd.DataFrame(st.session_state.mood_history)
            if not df.empty and 'sentiment_score' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                st.line_chart(df.set_index('timestamp')['sentiment_score'])
        except:
            pass
    
    st.markdown("---")
    
    st.header("🧘 Relaxation Tips")
    if st.button("Get a Tip"):
        st.info(f"💡 {st.session_state.tips.get_random_tip()}")
    
    st.markdown("---")
    
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.session_state.mood_history = []
        st.rerun()

# Chat Area
st.header("💬 Chat")

# Display messages
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.chat_message("user").write(msg['content'])
    else:
        with st.chat_message("assistant"):
            st.write(msg['content'])
            if 'mood' in msg:
                mood = msg['mood']
                colors = {'positive': '🟢', 'neutral': '🟡', 'negative': '🔴'}
                st.caption(f"Mood: {colors.get(mood, '⚪')} {mood.upper()}")

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({
        'role': 'user', 
        'content': user_input, 
        'timestamp': datetime.now().isoformat()
    })
    
    sentiment = st.session_state.analyzer.analyze(user_input)
    
    history = st.session_state.messages[:-1] if len(st.session_state.messages) > 1 else []
    response = st.session_state.chatbot.get_response(user_input, sentiment, history)
    
    st.session_state.messages.append({
        'role': 'assistant', 
        'content': response,
        'mood': sentiment['sentiment'],
        'sentiment_score': sentiment['score'],
        'timestamp': datetime.now().isoformat()
    })
    
    st.session_state.mood_history.append({
        'timestamp': datetime.now().isoformat(),
        'sentiment': sentiment['sentiment'],
        'sentiment_score': sentiment['score']
    })
    
    st.rerun()
