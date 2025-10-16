# question_maker_with_extraction.py
from keyword_extractor import LegislationExtractor

class AdaptiveQuestionMaker:
    def __init__(self):
        self.extractor = LegislationExtractor()
    
    def generate_from_user_input(self, user_input):
        """Main method: user input → legislation mapping → questions"""
        # Step 1: Extract from user input
        user_data = self.extractor.extract_from_user_input(user_input)
        print(f"🔍 User keywords: {user_data['keywords']}")
        print(f"🎭 User sentiment: {user_data['sentiment']}")
        
        # Step 2: Find relevant legislation
        relevant_bills = self.find_relevant_bills(user_data['keywords'])
        
        # Step 3: Generate questions based on findings
        questions = self.generate_questions(relevant_bills, user_data)
        
        return questions
    
    def find_relevant_bills(self, user_keywords, threshold=2):
        """Find bills that match user's keywords"""
        all_bills = self.extractor.extract_from_bill(limit=20)  # Get more bills to search
        relevant_bills = []
        
        for bill in all_bills:
            bill_keywords = [kw[0] for kw in bill['keywords']]  # Extract just the words
            matches = set(user_keywords) & set(bill_keywords)
            
            if len(matches) >= threshold:
                bill['match_score'] = len(matches)
                bill['matching_keywords'] = list(matches)
                relevant_bills.append(bill)
        
        # Sort by relevance
        relevant_bills.sort(key=lambda x: x['match_score'], reverse=True)
        return relevant_bills[:3]  # Top 3 most relevant
    
    def generate_questions(self, relevant_bills, user_data):
        """Generate questions using your existing question styles"""
        questions = []
        
        for bill in relevant_bills:
            # Use different question styles based on user sentiment
            if user_data['sentiment'] == 'negative':
                questions.extend(self.generate_emotional_questions(bill, 'negative'))
            elif user_data['sentiment'] == 'positive':
                questions.extend(self.generate_emotional_questions(bill, 'positive'))
            else:
                questions.extend(self.generate_factual_questions(bill))
            
            # Add a tradeoff question
            questions.extend(self.generate_tradeoff_questions(bill))
        
        return questions
    
    def generate_emotional_questions(self, bill, sentiment):
        """Like your question_maker2.py style"""
        emotion = "angry" if sentiment == 'negative' else "hopeful"
        
        return [{
            'type': 'emotional',
            'text': f"How {emotion} does '{bill['title']}' make you feel?",
            'bill_id': bill['bill_id'],
            'options': ['Very ' + emotion, 'Somewhat ' + emotion, 'Neutral', 'Not ' + emotion]
        }]
    
    def generate_factual_questions(self, bill):
        """Like your question_maker.py style"""
        # Use the top keyword from the bill
        top_keyword = bill['keywords'][0][0] if bill['keywords'] else 'this legislation'
        
        return [{
            'type': 'factual', 
            'text': f"Does '{bill['title']}' primarily address issues related to {top_keyword}?",
            'bill_id': bill['bill_id'],
            'options': ['Yes', 'No', 'Unsure']
        }]
    
    def generate_tradeoff_questions(self, bill):
        """Like your question_maker3.py style"""
        if len(bill['keywords']) >= 2:
            kw1, kw2 = bill['keywords'][0][0], bill['keywords'][1][0]
            return [{
                'type': 'tradeoff',
                'text': f"Should '{bill['title']}' prioritize {kw1} over {kw2}?",
                'bill_id': bill['bill_id'],
                'options': [f'Prioritize {kw1}', f'Prioritize {kw2}', 'Balanced approach']
            }]
        return []
