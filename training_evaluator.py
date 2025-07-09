import openai
import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TennisTrainingLog:
    """Tennis-specific training session data"""
    drills_trained: List[str]  # Multiple drills from: Forehand, Backhand, Serve, Slice, Dropshot, Volley, Return
    intensity: str  # Light, Moderate, Intense
    form_rating: str  # Poor, Average, Good, Excellent
    fatigue_level: str  # Low, Medium, High

@dataclass
class TennisDailyPlan:
    """Tennis-specific daily plan with recommendations"""
    hardcoded_suggestions: List[str]
    gpt_suggestions: Dict[str, Any]
    raw_gpt_response: str

class TennisTrainingEvaluator:
    """Tennis-specific training evaluator with hardcoded rules and AI integration"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Tennis drill categories for better recommendations
        self.basic_drills = ["Forehand", "Backhand", "Serve"]
        self.advanced_drills = ["Slice", "Dropshot", "Volley", "Return"]
        
    def create_daily_plan(self, tennis_log: TennisTrainingLog) -> TennisDailyPlan:
        """Generate a complete tennis training plan based on yesterday's session"""
        
        # Generate hardcoded tennis-specific suggestions
        hardcoded_suggestions = self._generate_tennis_hardcoded_suggestions(tennis_log)
        
        # Generate AI-powered tennis recommendations
        gpt_suggestions, raw_response = self._generate_tennis_gpt_suggestions(tennis_log)
        
        return TennisDailyPlan(
            hardcoded_suggestions=hardcoded_suggestions,
            gpt_suggestions=gpt_suggestions,
            raw_gpt_response=raw_response
        )
    
    def _generate_tennis_hardcoded_suggestions(self, tennis_log: TennisTrainingLog) -> List[str]:
        """Generate tennis-specific hardcoded recommendations based on training rules"""
        suggestions = []
        
        # Fatigue and intensity management
        if tennis_log.intensity == "Intense" and tennis_log.fatigue_level == "High":
            suggestions.append("🛌 Take a rest day or focus on light recovery exercises (gentle stretching, light footwork)")
            suggestions.append("💧 Emphasize hydration and proper nutrition for recovery")
        elif tennis_log.fatigue_level == "High":
            suggestions.append("⚡ Reduce training intensity today - focus on technique over power")
            suggestions.append("🎯 Work on mental game and strategy instead of physical drills")
        
        # Form/technique recommendations
        if tennis_log.form_rating == "Poor":
            suggestions.append(f"📚 Repeat yesterday's drills ({', '.join(tennis_log.drills_trained)}) with focus on proper technique")
            suggestions.append("🎥 Consider video analysis or working with a coach on form correction")
            suggestions.append("🐌 Slow down stroke speed to perfect technique before adding power")
        elif tennis_log.form_rating == "Average":
            suggestions.append("🔧 Include technique refinement drills for yesterday's practiced strokes")
            suggestions.append("🎯 Focus on consistency over power in today's session")
        
        # Drill balance and progression
        advanced_drills_trained = [drill for drill in tennis_log.drills_trained if drill in self.advanced_drills]
        basic_drills_trained = [drill for drill in tennis_log.drills_trained if drill in self.basic_drills]
        
        if len(advanced_drills_trained) >= 3:
            suggestions.append("⚖️ Balance today with fundamental drills (Forehand, Backhand, Serve) to maintain solid foundation")
            suggestions.append("🎯 Focus on court positioning and footwork fundamentals")
        
        if len(tennis_log.drills_trained) >= 5:
            suggestions.append("🎪 You trained many drills yesterday - consider focusing on 2-3 key areas today for deeper practice")
        
        # Specific drill recommendations
        if "Serve" in tennis_log.drills_trained and tennis_log.intensity == "Intense":
            suggestions.append("🎾 Include shoulder and arm recovery exercises - serving is demanding on these muscles")
        
        if "Volley" in tennis_log.drills_trained or "Return" in tennis_log.drills_trained:
            suggestions.append("⚡ Practice reaction time and quick decision-making drills")
        
        if "Slice" in tennis_log.drills_trained or "Dropshot" in tennis_log.drills_trained:
            suggestions.append("🎨 Continue touch and finesse work - these skills require consistent practice")
        
        # Intensity progression
        if tennis_log.intensity == "Light" and tennis_log.fatigue_level == "Low":
            suggestions.append("📈 You can safely increase intensity today - your body is ready for more challenge")
        elif tennis_log.intensity == "Intense" and tennis_log.fatigue_level == "Low":
            suggestions.append("💪 Great recovery! You can maintain high intensity if form stays good")
        
        # Ensure we always have suggestions
        if not suggestions:
            suggestions.append("🎾 Continue building on yesterday's progress with consistent practice")
            suggestions.append("🎯 Focus on one key area for improvement in today's session")
        
        return suggestions
    
    def _generate_tennis_gpt_suggestions(self, tennis_log: TennisTrainingLog) -> tuple[Dict[str, Any], str]:
        """Generate AI-powered tennis training recommendations using OpenAI"""
        
        # Create tennis-specific prompt
        prompt = f"""You are an expert tennis training coach with extensive experience in player development. 
        
Analyze this tennis training session from yesterday:

TRAINING SESSION DATA:
- Drills Practiced: {', '.join(tennis_log.drills_trained)}
- Training Intensity: {tennis_log.intensity}
- Form/Technique Rating: {tennis_log.form_rating}
- Fatigue Level After Session: {tennis_log.fatigue_level}

Based on this session data, provide a detailed analysis and recommendations for today's training. Structure your response as follows:

TODAYS_PLAN: [Specific drills and exercises for today's session, including duration and intensity recommendations]

DAILY_GOALS: [3-4 specific, actionable goals for today's training session]

WARNINGS: [Any precautions, injury prevention advice, or things to avoid based on yesterday's session]

REST_SUGGESTIONS: [Recovery activities, rest periods, and preparation advice for optimal performance]

Consider tennis-specific factors like:
- Stroke mechanics and muscle groups used
- Court movement and footwork
- Mental game and strategy
- Progressive skill development
- Injury prevention for tennis players
- Seasonal training considerations

Provide practical, actionable advice that a tennis player can immediately implement."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional tennis coach with 20+ years of experience training players at all levels."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            raw_response = response.choices[0].message.content
            
            # Parse the structured response
            suggestions = self._parse_tennis_gpt_response(raw_response)
            
            return suggestions, raw_response
            
        except Exception as e:
            # Fallback if API fails
            fallback_suggestions = {
                "todays_plan": f"Focus on refining the drills from yesterday: {', '.join(tennis_log.drills_trained)}. Adjust intensity based on your current fatigue level.",
                "daily_goals": "Improve stroke consistency, maintain proper form, and build court confidence.",
                "warnings": "Monitor fatigue levels and stop if form deteriorates significantly.",
                "rest_suggestions": "Include proper warm-up, cool-down, and hydration."
            }
            
            return fallback_suggestions, f"Error accessing AI recommendations: {str(e)}"
    
    def _parse_tennis_gpt_response(self, response: str) -> Dict[str, Any]:
        """Parse the structured GPT response for tennis recommendations"""
        suggestions = {}
        
        # Extract sections using keywords
        sections = {
            "todays_plan": ["TODAYS_PLAN:", "TODAY'S_PLAN:", "TODAYS PLAN:", "TODAY'S PLAN:"],
            "daily_goals": ["DAILY_GOALS:", "DAILY GOALS:", "GOALS:"],
            "warnings": ["WARNINGS:", "PRECAUTIONS:", "CAUTIONS:"],
            "rest_suggestions": ["REST_SUGGESTIONS:", "REST SUGGESTIONS:", "RECOVERY:", "REST:"]
        }
        
        for key, keywords in sections.items():
            for keyword in keywords:
                if keyword in response:
                    # Find the section content
                    start_idx = response.find(keyword) + len(keyword)
                    # Find the next section or end of response
                    next_section_idx = len(response)
                    for other_key, other_keywords in sections.items():
                        if other_key != key:
                            for other_keyword in other_keywords:
                                if other_keyword in response[start_idx:]:
                                    idx = response.find(other_keyword, start_idx)
                                    if idx != -1 and idx < next_section_idx:
                                        next_section_idx = idx
                    
                    content = response[start_idx:next_section_idx].strip()
                    suggestions[key] = content
                    break
        
        # Provide defaults if parsing fails
        if not suggestions.get("todays_plan"):
            suggestions["todays_plan"] = "Continue practicing fundamentals with focus on form and consistency."
        if not suggestions.get("daily_goals"):
            suggestions["daily_goals"] = "Improve stroke technique and court positioning."
        if not suggestions.get("warnings"):
            suggestions["warnings"] = "None - maintain good form throughout the session."
        if not suggestions.get("rest_suggestions"):
            suggestions["rest_suggestions"] = "Include proper warm-up, cool-down, and hydration."
        
        return suggestions

class TennisCoachBot:
    """Tennis-specific conversational coach for follow-up questions"""
    
    def __init__(self, tennis_plan: TennisDailyPlan, tennis_log: TennisTrainingLog):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.tennis_plan = tennis_plan
        self.tennis_log = tennis_log
        
    def ask_question(self, question: str) -> str:
        """Answer tennis-specific questions about the daily plan"""
        
        context = f"""
        YESTERDAY'S TENNIS SESSION:
        - Drills Practiced: {', '.join(self.tennis_log.drills_trained)}
        - Training Intensity: {self.tennis_log.intensity}
        - Form Rating: {self.tennis_log.form_rating}
        - Fatigue Level: {self.tennis_log.fatigue_level}
        
        TODAY'S RECOMMENDED PLAN:
        - Suggested Drills: {self.tennis_plan.gpt_suggestions.get('todays_plan', 'N/A')}
        - Daily Goals: {self.tennis_plan.gpt_suggestions.get('daily_goals', 'N/A')}
        - Warnings: {self.tennis_plan.gpt_suggestions.get('warnings', 'N/A')}
        - Recovery: {self.tennis_plan.gpt_suggestions.get('rest_suggestions', 'N/A')}
        
        HARDCODED RECOMMENDATIONS:
        {' | '.join(self.tennis_plan.hardcoded_suggestions)}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable tennis coach. Answer questions about tennis training plans using the provided context. Be specific, practical, and encouraging. Focus on tennis technique, strategy, and player development."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I'm having trouble accessing my tennis knowledge right now. Please try asking your question again, or refer to the written recommendations above. Error: {str(e)}" 