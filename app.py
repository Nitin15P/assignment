import streamlit as st
import os
from dotenv import load_dotenv
from training_evaluator import TennisTrainingEvaluator, TennisCoachBot, TennisTrainingLog
import json

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title=os.getenv('STREAMLIT_PAGE_TITLE', 'Tennis Training Evaluator'),
    page_icon=os.getenv('STREAMLIT_PAGE_ICON', '🎾'),
    layout=os.getenv('STREAMLIT_LAYOUT', 'wide'),
    initial_sidebar_state=os.getenv('STREAMLIT_SIDEBAR_STATE', 'expanded')
)

def main():
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    /* Adjust the main container for better layout */
    .main .block-container {
        max-width: none !important;
        padding-right: 1rem !important;
    }
    
    /* Style for CoachBot section when expanded */
    .coach-section {
        background: linear-gradient(180deg, rgba(15, 15, 35, 0.1) 0%, rgba(25, 25, 45, 0.1) 100%);
        border: 2px solid #1c83e1;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'tennis_plan' not in st.session_state:
        st.session_state.tennis_plan = None
    if 'tennis_log' not in st.session_state:
        st.session_state.tennis_log = None
    if 'tennis_coach_bot' not in st.session_state:
        st.session_state.tennis_coach_bot = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'coach_panel_open' not in st.session_state:
        st.session_state.coach_panel_open = False
    
    # Main content (now uses full width)
    st.title("🎾 Tennis Training Evaluator & Daily Planner")
    st.markdown("AI-powered tennis training analysis and personalized daily planning assistant")
    
    # Sidebar for configuration and help
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check if OpenAI API key is configured
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            st.error("🔑 OpenAI API Key not configured!")
            st.info("Please add your OpenAI API key to the .env file")
            st.code("OPENAI_API_KEY=your_actual_api_key_here")
        else:
            st.success("🔑 OpenAI API Key configured")
        
        st.subheader("📖 How to Use")
        st.markdown("""
        1. **Select Tennis Drills**: Choose which drills you practiced yesterday
        2. **Rate Your Session**: Input intensity, form rating, and fatigue level
        3. **Generate Plan**: Get tennis-specific recommendations for today
        4. **Ask TennisBot**: Use the AI coach for follow-up questions
        5. **Export Results**: Download your personalized tennis plan
        """)
        
        st.subheader("🎾 Tennis Training Categories")
        
        st.write("**Available Drills:**")
        st.write("• **Basic**: Forehand, Backhand, Serve")
        st.write("• **Advanced**: Slice, Dropshot, Volley, Return")
        st.write("**Intensity Levels:** Light, Moderate, Intense")
        st.write("**Form Ratings:** Poor, Average, Good, Excellent")
        st.write("**Fatigue Levels:** Low, Medium, High")
    
    # Main content area - Tennis-specific inputs
    st.header("🏆 Yesterday's Tennis Training Session")
    st.markdown("Enter the details from your tennis training session yesterday:")
    
    # Tennis drill selection
    st.subheader("🎯 Drills Practiced")
    
    # Available tennis drills
    available_drills = ["Forehand", "Backhand", "Serve", "Slice", "Dropshot", "Volley", "Return"]
    
    drills_trained = st.multiselect(
        "Select all drills you practiced yesterday:",
        options=available_drills,
        default=[],
        help="Choose all the tennis drills you worked on in yesterday's session"
    )
    
    # Tennis session metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        intensity = st.selectbox(
            "⚡ Training Intensity",
            options=["Light", "Moderate", "Intense"],
            help="How intense was your overall training session?"
        )
    
    with col2:
        form_rating = st.selectbox(
            "📈 Form/Technique Rating", 
            options=["Poor", "Average", "Good", "Excellent"],
            help="How would you rate your form and technique during the session?"
        )
    
    with col3:
        fatigue_level = st.selectbox(
            "😴 Fatigue Level After Session",
            options=["Low", "Medium", "High"],
            help="How tired did you feel after completing the session?"
        )
    
    # Alternative JSON input for advanced users
    st.subheader("🔧 Alternative: JSON Input")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        json_input = st.text_area(
            "Enter tennis training data as JSON (optional)",
            placeholder='{"drills_trained": ["Forehand", "Backhand", "Serve"], "intensity": "Moderate", "form_rating": "Good", "fatigue_level": "Medium"}',
            height=100
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Load from JSON"):
            try:
                data = json.loads(json_input)
                required_keys = ['drills_trained', 'intensity', 'form_rating', 'fatigue_level']
                if all(key in data for key in required_keys):
                    drills_trained = data['drills_trained']
                    intensity = data['intensity']
                    form_rating = data['form_rating']
                    fatigue_level = data['fatigue_level']
                    st.success("✅ Tennis training data loaded successfully!")
                else:
                    st.error(f"❌ JSON must contain: {', '.join(required_keys)}")
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format")
    
    # Generate tennis daily plan
    if st.button("🚀 Generate Today's Tennis Plan", type="primary"):
        if not api_key or api_key == 'your_openai_api_key_here':
            st.error("Please configure your OpenAI API key first!")
            return
        
        if not drills_trained:
            st.warning("Please select at least one drill you practiced yesterday!")
            return
        
        # Create tennis training log
        tennis_log = TennisTrainingLog(
            drills_trained=drills_trained,
            intensity=intensity,
            form_rating=form_rating,
            fatigue_level=fatigue_level
        )
        
        st.session_state.tennis_log = tennis_log
        
        # Generate tennis plan
        with st.spinner("🎾 Analyzing your tennis session and generating personalized recommendations..."):
            evaluator = TennisTrainingEvaluator()
            tennis_plan = evaluator.create_daily_plan(tennis_log)
            st.session_state.tennis_plan = tennis_plan
            
            # Initialize TennisCoachBot
            st.session_state.tennis_coach_bot = TennisCoachBot(tennis_plan, tennis_log)
            st.session_state.chat_history = []
            
            # Auto scroll to daily plan section
            st.session_state.show_plan = True
        
        st.success("✅ Your personalized tennis training plan is ready!")
        st.info("🎾 TennisBot is now available! Click the button below to start chatting about your plan.")
        st.balloons()

    # Show Tennis Daily Plan section if generated
    if st.session_state.tennis_plan is not None:
        st.divider()
        st.header("🏆 Your Personalized Tennis Training Plan")
        
        tennis_plan = st.session_state.tennis_plan
        tennis_log = st.session_state.tennis_log
        
        # Tennis session summary
        st.subheader("📊 Yesterday's Tennis Session Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Drills Practiced", f"{len(tennis_log.drills_trained)} drills")
        with col2:
            st.metric("⚡ Intensity", tennis_log.intensity)
        with col3:
            st.metric("📈 Form Rating", tennis_log.form_rating)
        with col4:
            st.metric("😴 Fatigue Level", tennis_log.fatigue_level)
        
        # Display drills practiced
        st.markdown("**Drills Practiced:**")
        drill_cols = st.columns(len(tennis_log.drills_trained))
        for i, drill in enumerate(tennis_log.drills_trained):
            with drill_cols[i]:
                st.info(f"🎾 {drill}")
        
        st.divider()
        
        # Rule-based tennis recommendations
        st.subheader("🧠 Tennis-Specific Rule-Based Recommendations")
        st.markdown("*Generated using proven tennis training principles and coaching expertise*")
        
        for i, suggestion in enumerate(tennis_plan.hardcoded_suggestions, 1):
            st.markdown(f"**{i}.** {suggestion}")
        
        st.divider()
        
        # AI-powered tennis recommendations
        st.subheader("🤖 AI-Powered Tennis Coach Recommendations")
        st.markdown("*Generated using advanced tennis training analysis*")
        
        # Today's Tennis Plan - Full width
        st.markdown("### 🎾 Today's Training Session Plan")
        if tennis_plan.gpt_suggestions.get('todays_plan'):
            st.info(tennis_plan.gpt_suggestions['todays_plan'])
        else:
            st.info("No specific training plan generated.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Daily Tennis Goals")
            if tennis_plan.gpt_suggestions.get('daily_goals'):
                st.markdown(tennis_plan.gpt_suggestions['daily_goals'])
            else:
                st.info("No specific daily goals generated.")
            
            st.markdown("### ⚠️ Warnings & Precautions")
            if tennis_plan.gpt_suggestions.get('warnings'):
                if tennis_plan.gpt_suggestions['warnings'].lower() != 'none':
                    st.warning(tennis_plan.gpt_suggestions['warnings'])
                else:
                    st.success("No warnings - you're ready to play!")
            else:
                st.info("No warnings available.")
        
        with col2:
            st.markdown("### 🛌 Recovery & Rest Suggestions")
            if tennis_plan.gpt_suggestions.get('rest_suggestions'):
                st.markdown(tennis_plan.gpt_suggestions['rest_suggestions'])
            else:
                st.info("No specific recovery suggestions generated.")
        
        # Raw GPT response (expandable)
        with st.expander("🔍 View Full AI Tennis Analysis"):
            st.text(tennis_plan.raw_gpt_response)
        
        # Export functionality
        st.divider()
        st.subheader("📤 Export Your Tennis Plan")
        
        plan_date = st.date_input("Plan Date", value=None, key="plan_date_export")
        
        # Create a nicely formatted text version for tennis
        date_str = plan_date.isoformat() if plan_date else "today"
        
        export_text = f"""
# TENNIS TRAINING PLAN
Generated on: {date_str}

## YESTERDAY'S TENNIS SESSION SUMMARY
• Drills Practiced: {', '.join(tennis_log.drills_trained)}
• Training Intensity: {tennis_log.intensity}
• Form/Technique Rating: {tennis_log.form_rating}
• Fatigue Level: {tennis_log.fatigue_level}

## TENNIS-SPECIFIC RULE-BASED RECOMMENDATIONS
Generated using proven tennis training principles:

"""
        
        for i, suggestion in enumerate(tennis_plan.hardcoded_suggestions, 1):
            export_text += f"{i}. {suggestion}\n"
        
        export_text += f"""
## AI-POWERED TENNIS COACH RECOMMENDATIONS
Generated using advanced tennis training analysis:

### Today's Training Session Plan
{tennis_plan.gpt_suggestions.get('todays_plan', 'No specific training plan generated.')}

### Daily Tennis Goals
{tennis_plan.gpt_suggestions.get('daily_goals', 'No specific daily goals generated.')}

### Warnings & Precautions
{tennis_plan.gpt_suggestions.get('warnings', 'No warnings available.')}

### Recovery & Rest Suggestions
{tennis_plan.gpt_suggestions.get('rest_suggestions', 'No specific recovery suggestions generated.')}

## FULL AI TENNIS ANALYSIS
{tennis_plan.raw_gpt_response}

---
Generated by Tennis Training Evaluator & Daily Planner
🎾 Keep improving your game!
"""
        
        st.download_button(
            label="🎾 Download Tennis Plan as Text",
            data=export_text,
            file_name=f"tennis_training_plan_{date_str}.txt",
            mime="text/plain"
        )
    
    # Tennis CoachBot toggle button and panel
    if st.session_state.tennis_coach_bot is not None:
        # Create a simple toggle button
        if st.button("🎾 TennisBot - Your AI Tennis Coach", key="tennis_coach_toggle", help="Chat with your AI Tennis Coach"):
            st.session_state.coach_panel_open = not st.session_state.coach_panel_open
            st.rerun()
        
        # TennisCoachBot panel (conditionally shown)
        if st.session_state.coach_panel_open:
            st.divider()
            
            # Clean header for the tennis chatbot section
            col1, col2 = st.columns([10, 1])
            with col1:
                st.header("🎾 TennisBot - Your AI Tennis Coach")
            with col2:
                if st.button("✕", key="tennis_coach_close", help="Close TennisBot"):
                    st.session_state.coach_panel_open = False
                    st.rerun()
            
            st.markdown("Ask me anything about your tennis training plan!")
            
            # Tennis-specific quick question buttons
            st.subheader("🎾 Quick Tennis Questions")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Why should I practice this drill again?", key="tennis_quick1", use_container_width=True):
                    question = "Why should I practice this drill again?"
                    answer = st.session_state.tennis_coach_bot.ask_question(question)
                    st.session_state.chat_history.append((question, answer))
                    st.rerun()
                
                if st.button("Can I skip my session tomorrow?", key="tennis_quick2", use_container_width=True):
                    question = "Can I skip my tennis session tomorrow?"
                    answer = st.session_state.tennis_coach_bot.ask_question(question)
                    st.session_state.chat_history.append((question, answer))
                    st.rerun()
            
            with col2:
                if st.button("What's my main focus for the next session?", key="tennis_quick3", use_container_width=True):
                    question = "What's my main focus for the next tennis session?"
                    answer = st.session_state.tennis_coach_bot.ask_question(question)
                    st.session_state.chat_history.append((question, answer))
                    st.rerun()
                
                if st.button("How can I improve my weak areas?", key="tennis_quick4", use_container_width=True):
                    question = "How can I improve my weak areas in tennis?"
                    answer = st.session_state.tennis_coach_bot.ask_question(question)
                    st.session_state.chat_history.append((question, answer))
                    st.rerun()
            
            # Custom tennis question input
            st.subheader("❓ Ask Your Tennis Coach")
            with st.form("tennis_coach_form"):
                user_question = st.text_area(
                    "Your tennis question:",
                    placeholder="e.g., How can I improve my backhand consistency? Should I focus more on serves or returns?",
                    height=80,
                    label_visibility="collapsed",
                    key="tennis_question_input"
                )
                
                submitted = st.form_submit_button("🎾 Ask TennisBot", use_container_width=True)
                
                if submitted and user_question.strip():
                    # Simple validation - only respond to actual questions
                    if len(user_question.strip()) > 2 and any(char in user_question.lower() for char in ['?', 'how', 'what', 'why', 'when', 'should', 'can', 'is', 'are']):
                        with st.spinner("🎾 TennisBot is analyzing your question..."):
                            answer = st.session_state.tennis_coach_bot.ask_question(user_question)
                            st.session_state.chat_history.append((user_question, answer))
                            st.rerun()
                    else:
                        st.warning("Please ask a specific question about your tennis training plan.")
            
            # Display tennis chat history
            if st.session_state.chat_history:
                st.subheader("🎾 Tennis Coaching Conversation History")
                
                # Show all conversations in a clean format
                for i, (question, answer) in enumerate(reversed(st.session_state.chat_history)):
                    with st.expander(f"Q{len(st.session_state.chat_history)-i}: {question[:40]}..."):
                        st.markdown(f"**You:** {question}")
                        st.markdown("---")
                        st.markdown(f"**TennisBot:** {answer}")
                
                if st.button("🗑️ Clear Chat History", key="tennis_clear", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            else:
                st.info("🎾 No conversations yet. Ask a tennis question above!")

if __name__ == "__main__":
    main() 