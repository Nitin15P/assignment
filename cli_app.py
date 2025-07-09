#!/usr/bin/env python3
"""
Command Line Interface for Training Evaluator
Run with: python cli_app.py
"""

import os
import json
from dotenv import load_dotenv
from training_evaluator import TrainingEvaluator, CoachBot, TrainingLog

# Load environment variables
load_dotenv()

def print_header():
    """Print application header"""
    print("=" * 60)
    print(f"🏃‍♂️ {os.getenv('APP_TITLE', 'Training Evaluator & Daily Planner')}")
    print(f"{os.getenv('APP_DESCRIPTION', 'AI-powered training log analysis')}")
    print("=" * 60)

def print_section_header(title):
    """Print section header"""
    print(f"\n{'='*20} {title} {'='*20}")

def get_training_input():
    """Get training input from user"""
    print_section_header("YESTERDAY'S TRAINING INPUT")
    
    # Get pace options from environment
    pace_options = os.getenv('PACE_OPTIONS', 'slow,moderate,fast').split(',')
    load_options = os.getenv('LOAD_OPTIONS', 'low,medium,high').split(',')
    accuracy_options = os.getenv('ACCURACY_OPTIONS', 'poor,average,good,excellent').split(',')
    
    print(f"Pace options: {', '.join(pace_options)}")
    print(f"Load options: {', '.join(load_options)}")
    print(f"Accuracy options: {', '.join(accuracy_options)}")
    
    # Option 1: Manual input
    print("\n📝 Option 1: Manual Input")
    
    while True:
        pace = input(f"🏃 Training Pace ({'/'.join(pace_options)}): ").strip().lower()
        if pace in pace_options:
            break
        print(f"❌ Invalid option. Choose from: {', '.join(pace_options)}")
    
    while True:
        load = input(f"💪 Training Load ({'/'.join(load_options)}): ").strip().lower()
        if load in load_options:
            break
        print(f"❌ Invalid option. Choose from: {', '.join(load_options)}")
    
    while True:
        video_accuracy = input(f"📹 Video Accuracy ({'/'.join(accuracy_options)}): ").strip().lower()
        if video_accuracy in accuracy_options:
            break
        print(f"❌ Invalid option. Choose from: {', '.join(accuracy_options)}")
    
    return TrainingLog(pace=pace, load=load, video_accuracy=video_accuracy)

def get_json_input():
    """Get training input from JSON"""
    print("\n📋 Option 2: JSON Input")
    print("Enter JSON data (or press Enter to skip):")
    print("Example: {\"pace\": \"moderate\", \"load\": \"high\", \"video_accuracy\": \"good\"}")
    
    json_input = input("JSON: ").strip()
    
    if not json_input:
        return None
    
    try:
        data = json.loads(json_input)
        if all(key in data for key in ['pace', 'load', 'video_accuracy']):
            return TrainingLog(
                pace=data['pace'],
                load=data['load'],
                video_accuracy=data['video_accuracy']
            )
        else:
            print("❌ JSON must contain: pace, load, video_accuracy")
            return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON format")
        return None

def display_daily_plan(daily_plan, training_log):
    """Display the generated daily plan"""
    print_section_header("YOUR DAILY PLAN")
    
    # Performance summary
    print("📊 YESTERDAY'S PERFORMANCE SUMMARY:")
    print(f"  🏃 Pace: {training_log.pace.title()}")
    print(f"  💪 Load: {training_log.load.title()}")
    print(f"  📹 Video Accuracy: {training_log.video_accuracy.title()}")
    
    # Hardcoded suggestions
    print("\n🔧 RULE-BASED RECOMMENDATIONS:")
    print("   (Generated using proven training principles)")
    for i, suggestion in enumerate(daily_plan.hardcoded_suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    # GPT suggestions
    print("\n🤖 AI-POWERED RECOMMENDATIONS:")
    print("   (Generated using advanced prompt-based reasoning)")
    
    if daily_plan.gpt_suggestions.get('daily_goals'):
        print(f"\n   🎯 DAILY GOALS:")
        print(f"   {daily_plan.gpt_suggestions['daily_goals']}")
    
    if daily_plan.gpt_suggestions.get('rest_suggestions'):
        print(f"\n   🛌 REST & RECOVERY:")
        print(f"   {daily_plan.gpt_suggestions['rest_suggestions']}")
    
    if daily_plan.gpt_suggestions.get('warnings'):
        print(f"\n   ⚠️  WARNINGS:")
        if daily_plan.gpt_suggestions['warnings'].lower() != 'none':
            print(f"   {daily_plan.gpt_suggestions['warnings']}")
        else:
            print("   No warnings - you're good to go!")

def coach_bot_session(coach_bot):
    """Interactive CoachBot session"""
    print_section_header("COACHBOT CONVERSATION")
    print("🤖 Ask me questions about your daily plan!")
    print("💡 Suggested questions:")
    print("   - Why am I doing video drills?")
    print("   - Can I skip today's training?")
    print("   - What is my main goal today?")
    print("   - How should I modify training if I'm tired?")
    print("\nType 'quit' or 'exit' to return to main menu.\n")
    
    while True:
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            print("Please enter a question or 'quit' to exit.")
            continue
        
        print("🤔 CoachBot is thinking...")
        answer = coach_bot.ask_question(question)
        print(f"🤖 CoachBot: {answer}\n")

def save_plan_to_file(daily_plan, training_log):
    """Save daily plan to JSON file"""
    filename = input("💾 Enter filename (without .json extension): ").strip()
    if not filename:
        filename = "daily_plan"
    
    filename = f"{filename}.json"
    
    export_data = {
        "date": "today",
        "yesterday_performance": {
            "pace": training_log.pace,
            "load": training_log.load,
            "video_accuracy": training_log.video_accuracy
        },
        "hardcoded_suggestions": daily_plan.hardcoded_suggestions,
        "ai_suggestions": daily_plan.gpt_suggestions,
        "full_ai_response": daily_plan.raw_gpt_response
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"✅ Daily plan saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

def main():
    """Main application loop"""
    print_header()
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ ERROR: OpenAI API Key not configured!")
        print("Please create a .env file and add your OpenAI API key:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        return
    
    print("✅ OpenAI API Key configured")
    
    # Get training input
    print("\nChoose input method:")
    print("1. Manual input (guided)")
    print("2. JSON input")
    
    choice = input("Select option (1 or 2): ").strip()
    
    training_log = None
    
    if choice == "1":
        training_log = get_training_input()
    elif choice == "2":
        training_log = get_json_input()
        if training_log is None:
            print("Falling back to manual input...")
            training_log = get_training_input()
    else:
        print("Invalid choice, using manual input...")
        training_log = get_training_input()
    
    # Generate daily plan
    print("\n🚀 Generating your personalized daily plan...")
    print("🤔 Analyzing training data and consulting AI coach...")
    
    try:
        evaluator = TrainingEvaluator()
        daily_plan = evaluator.create_daily_plan(training_log)
        
        # Display results
        display_daily_plan(daily_plan, training_log)
        
        # Initialize CoachBot
        coach_bot = CoachBot(daily_plan, training_log)
        
        # Interactive menu
        while True:
            print_section_header("WHAT WOULD YOU LIKE TO DO?")
            print("1. 🤖 Ask CoachBot questions")
            print("2. 💾 Save plan to file")
            print("3. 📋 View plan again")
            print("4. 🆕 Create new plan")
            print("5. 🚪 Exit")
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == "1":
                coach_bot_session(coach_bot)
            elif choice == "2":
                save_plan_to_file(daily_plan, training_log)
            elif choice == "3":
                display_daily_plan(daily_plan, training_log)
            elif choice == "4":
                print("🔄 Starting over...")
                main()
                return
            elif choice == "5":
                print("👋 Thank you for using Training Evaluator!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
    
    except Exception as e:
        print(f"❌ Error generating daily plan: {e}")
        print("Please check your OpenAI API key and internet connection.")

if __name__ == "__main__":
    main() 