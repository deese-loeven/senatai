# adaptive_survey.py
from keyword_extractor import WorkingExtractor
import random

class AdaptiveSurvey:
    def __init__(self):
        self.extractor = WorkingExtractor()
        self.question_styles = [
            self.emotional_questions,
            self.factual_questions, 
            self.tradeoff_questions,
            self.multiple_choice_questions
        ]
    
    def start_session(self):
        """Main survey session - natural language entry to questions"""
        print("\n" + "🔥" * 60)
        print("🔥              SENATAI - SPEAK YOUR MIND               🔥")
        print("🔥" * 60)
        
        # Engaging opening prompts
        prompts = [
            "🗳️  Vote booth now open - what's really on your mind?",
            "💬  Complain here - we'll turn it into actual change",
            "🤔  What's burning you up right now? Let 'em know!",
            "📢  They need to hear this - what's bothering you today?",
            "🎯  Select topic or just vent - we'll find the laws that matter"
        ]
        
        prompt = random.choice(prompts)
        user_input = input(f"\n{prompt}\n\n> ")
        
        if not user_input.strip():
            print("🤷 Come on, tell us what you really think!")
            return
        
        print(f"\n🔍 Searching for laws related to: '{user_input}'")
        
        # Extract user keywords
        user_keywords = self.extractor.extract_from_user(user_input)
        user_keyword_list = [kw[0] for kw in user_keywords]
        print(f"🎯 Your concerns: {user_keyword_list}")
        
        # Find relevant bills
        all_bills = self.extractor.get_bills_simple(10)  # Get more bills to match against
        relevant_bills = self.find_relevant_bills(all_bills, user_keyword_list)
        
        if not relevant_bills:
            print("🤔 No exact matches found, but here are some current bills you might care about:")
            relevant_bills = all_bills[:3]  # Show some recent bills anyway
        
        print(f"\n📚 Found {len(relevant_bills)} relevant laws")
        
        # Generate and ask questions
        self.ask_questions(relevant_bills, user_input)
        
        print(f"\n🎉 Thanks for making your voice heard! +3 Policaps earned!")
    
    def find_relevant_bills(self, bills, user_keywords):
        """Find bills that match user keywords"""
        relevant = []
        for bill in bills:
            bill_keywords = [kw[0] for kw in bill['keywords']]
            matches = set(user_keywords) & set(bill_keywords)
            if matches:
                bill['match_score'] = len(matches)
                bill['matching_keywords'] = list(matches)
                relevant.append(bill)
        
        # Sort by relevance
        relevant.sort(key=lambda x: x['match_score'], reverse=True)
        return relevant[:5]  # Top 5 most relevant
    
    def ask_questions(self, bills, user_input):
        """Generate and ask adaptive questions"""
        questions = []
        
        for i, bill in enumerate(bills):
            print(f"\n--- Question Set {i+1} about {bill['number']}: {bill['title']} ---")
            
            # Mix different question styles
            style = random.choice(self.question_styles)
            q_batch = style(bill, user_input)
            questions.extend(q_batch)
            
            # Ask this batch
            for j, q in enumerate(q_batch):
                print(f"\nQ{i+1}.{j+1}: {q['text']}")
                if 'options' in q:
                    for k, opt in enumerate(q['options']):
                        print(f"   {k+1}. {opt}")
                
                # Get answer
                answer = input("\nYour answer: ").strip()
                if answer.lower() in ['quit', 'exit', 'stop']:
                    return
                
                # Simple engagement tracking
                if answer and len(answer) > 1:
                    print("💡 Opinion recorded!")
    
    def emotional_questions(self, bill, user_input):
        """Like your question_maker2.py - emotional framing"""
        emotions = ['angry', 'hopeful', 'frustrated', 'optimistic', 'worried', 'excited']
        emotion = random.choice(emotions)
        
        return [{
            'type': 'emotional',
            'text': f"How {emotion} does '{bill['title']}' make you feel about {user_input.split()[0]}?",
            'bill': bill['number'],
            'options': [f'Very {emotion}', f'Somewhat {emotion}', 'Neutral', f'Not {emotion}']
        }]
    
    def factual_questions(self, bill, user_input):
        """Like your question_maker.py - factual verification"""
        if bill['keywords']:
            topic = bill['keywords'][0][0]
            return [{
                'type': 'factual',
                'text': f"Should '{bill['title']}' address issues like {topic}?",
                'bill': bill['number'], 
                'options': ['Yes, strongly', 'Yes, somewhat', 'No', 'Unsure']
            }]
        return []
    
    def tradeoff_questions(self, bill, user_input):
        """Like your question_maker3.py - value tradeoffs"""
        if len(bill['keywords']) >= 2:
            kw1, kw2 = bill['keywords'][0][0], bill['keywords'][1][0]
            return [{
                'type': 'tradeoff', 
                'text': f"Would you support '{bill['title']}' if it meant prioritizing {kw1} over {kw2}?",
                'bill': bill['number'],
                'options': [f'Prioritize {kw1}', f'Prioritize {kw2}', 'Find balance', 'Oppose either']
            }]
        return []
    
    def multiple_choice_questions(self, bill, user_input):
        """Like your question_maker6.py - structured responses"""
        return [{
            'type': 'multiple_choice',
            'text': f"How would you rate the importance of '{bill['title']}'?",
            'bill': bill['number'],
            'options': ['Essential', 'Important', 'Neutral', 'Unimportant', 'Harmful']
        }]

# Run the survey
def main():
    survey = AdaptiveSurvey()
    try:
        survey.start_session()
    finally:
        survey.extractor.close()

if __name__ == "__main__":
    main()
