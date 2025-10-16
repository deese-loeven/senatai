# adaptive_survey_enhanced.py
from keyword_extractor import WorkingExtractor
import random
import re

class EnhancedSurvey:
    def __init__(self):
        self.extractor = WorkingExtractor()
    
    def extract_user_concern(self, user_input):
        """Better extraction of the main concern"""
        # Common concern patterns
        patterns = {
            'cost_of_living': r'(cost of living|heating cost|price|afford|expensive)',
            'housing': r'(housing|rent|mortgage|home)',
            'family_support': r'(mom|parent|child|family|assistance|support)',
            'healthcare': r'(health|medical|doctor|hospital)'
        }
        
        for concern_type, pattern in patterns.items():
            if re.search(pattern, user_input.lower()):
                return concern_type.replace('_', ' ')
        
        return "these issues"
    
    def start_session(self):
        print("\n" + "🔥" * 60)
        print("🔥              SENATAI - WHAT'S ON YOUR MIND?           🔥")
        print("🔥" * 60)
        
        user_input = input("\n💬 What's bothering you today? We'll find the laws that matter.\n\n> ")
        
        if not user_input.strip():
            print("🤷 Come on, tell us what's really bothering you!")
            return
        
        user_concern = self.extract_user_concern(user_input)
        print(f"\n🔍 Looking for laws about {user_concern}...")
        
        # Get bills and ask better questions
        bills = self.extractor.get_bills_simple(8)
        self.ask_contextual_questions(bills, user_concern, user_input)
        
        print(f"\n🎉 Your voice matters! +3 Policaps earned!")
    
    def ask_contextual_questions(self, bills, user_concern, user_input):
        """Ask questions that actually relate to user's concern"""
        print(f"\n📋 Here are some current laws that might affect {user_concern}:")
        
        for i, bill in enumerate(bills[:4], 1):
            print(f"\n--- Law {i}: {bill['number']} - {bill['title']} ---")
            
            # Contextual question based on user concern
            if 'cost' in user_concern or 'afford' in user_input.lower():
                question = f"Would '{bill['title']}' help or hurt with {user_concern}?"
                options = ['Help significantly', 'Help somewhat', 'No effect', 'Hurt somewhat', 'Hurt significantly']
            elif 'family' in user_concern or 'mom' in user_input.lower():
                question = f"How would '{bill['title']}' affect families like yours?"
                options = ['Very positively', 'Somewhat positively', 'No effect', 'Somewhat negatively', 'Very negatively']
            else:
                question = f"What's your view on '{bill['title']}' regarding {user_concern}?"
                options = ['Strongly support', 'Somewhat support', 'Neutral', 'Somewhat oppose', 'Strongly oppose']
            
            print(f"Q{i}: {question}")
            for j, opt in enumerate(options, 1):
                print(f"   {j}. {opt}")
            
            answer = input("\nYour choice (1-5): ").strip()
            if answer and answer in ['1','2','3','4','5']:
                print(f"📝 Recorded: {options[int(answer)-1]}")
            else:
                print("💡 Skipped")

# Test the enhanced version
if __name__ == "__main__":
    survey = EnhancedSurvey()
    try:
        survey.start_session()
    finally:
        survey.extractor.close()
