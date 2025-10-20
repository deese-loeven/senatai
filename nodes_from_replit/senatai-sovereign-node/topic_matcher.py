import re

TOPIC_KEYWORDS = {
    'Environment': ['climate', 'carbon', 'emission', 'pollution', 'environment', 'green', 'renewable', 'fossil', 'oil', 'gas'],
    'Economy': ['tax', 'economy', 'money', 'budget', 'spending', 'revenue', 'fiscal', 'economic', 'jobs', 'employment', 'wage'],
    'Social Services': ['health', 'healthcare', 'hospital', 'disability', 'benefit', 'welfare', 'social', 'poverty', 'homeless'],
    'Media': ['internet', 'online', 'platform', 'social media', 'news', 'broadcasting', 'streaming', 'digital'],
    'Privacy': ['privacy', 'data', 'personal information', 'surveillance', 'tracking', 'security'],
    'Labor': ['worker', 'labor', 'labour', 'union', 'pension', 'workplace', 'employment', 'rights'],
    'Housing': ['housing', 'rent', 'landlord', 'tenant', 'mortgage', 'home', 'affordable', 'eviction'],
    'Family': ['family', 'child', 'childcare', 'daycare', 'parental', 'custody', 'children', 'parent'],
    'Justice': ['justice', 'court', 'legal', 'law', 'crime', 'police', 'prison', 'sentence'],
    'Immigration': ['immigration', 'immigrant', 'refugee', 'citizenship', 'border', 'visa'],
    'Education': ['education', 'school', 'teacher', 'student', 'university', 'college', 'tuition'],
    'Healthcare': ['healthcare', 'hospital', 'doctor', 'medical', 'medicine', 'drug', 'prescription'],
    'Indigenous': ['indigenous', 'first nations', 'aboriginal', 'treaty', 'reconciliation'],
    'Transportation': ['transport', 'transit', 'bus', 'train', 'highway', 'infrastructure', 'road'],
    'Agriculture': ['farm', 'agriculture', 'farmer', 'crop', 'livestock', 'rural'],
    'Gun Control': ['gun', 'firearm', 'weapon', 'shooting', 'rifle', 'handgun'],
    'Other': []
}


def extract_topics_from_text(complaint_text):
    """
    Extract relevant topics from complaint text using keyword matching.
    Returns list of matched categories.
    """
    text_lower = complaint_text.lower()
    matched_topics = []
    
    for category, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                if category not in matched_topics:
                    matched_topics.append(category)
                break
    
    if not matched_topics:
        matched_topics.append('Other')
    
    return matched_topics


def match_bills_to_complaint(complaint_text, all_bills):
    """
    Find bills that match the complaint's topics.
    Returns list of bill_ids that are relevant.
    """
    text_lower = complaint_text.lower()
    matched_bills = []
    
    for bill in all_bills:
        try:
            # Handle both sqlite3.Row and dict-like objects
            if hasattr(bill, 'keys'):
                bill_id = bill['bill_id']
                bill_title = bill['bill_title']
                bill_summary = bill['bill_summary']
                bill_category = bill['category'] if 'category' in bill.keys() else ''
            else:
                bill_id = bill[0]
                bill_title = bill[1]
                bill_summary = bill[2]
                bill_category = bill[4] if len(bill) > 4 else ''
        except (KeyError, IndexError, TypeError):
            continue
        
        # Check if complaint keywords appear in bill title or summary
        words = re.findall(r'\w+', text_lower)
        significant_words = [w for w in words if len(w) > 4]  # Words longer than 4 chars
        
        bill_text = f"{bill_title} {bill_summary}".lower()
        
        matches = 0
        for word in significant_words:
            if word in bill_text:
                matches += 1
        
        # Also match by category
        topics = extract_topics_from_text(complaint_text)
        if bill_category in topics:
            matches += 2
        
        if matches >= 2:  # At least 2 keyword matches or 1 category match
            matched_bills.append(bill_id)
    
    return matched_bills


def extract_complaint_summary(complaint_text, max_length=100):
    """
    Create a short summary of the complaint for display.
    """
    if len(complaint_text) <= max_length:
        return complaint_text
    
    return complaint_text[:max_length] + '...'


def get_trending_topics(complaints_list):
    """
    Analyze a list of complaints to find trending topics.
    Returns dict of {topic: count}
    """
    topic_counts = {}
    
    for complaint in complaints_list:
        try:
            if hasattr(complaint, 'keys'):
                complaint_text = complaint['complaint_text']
            else:
                complaint_text = complaint[1]
        except (KeyError, IndexError, TypeError):
            continue
            
        topics = extract_topics_from_text(complaint_text)
        
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    # Sort by count
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_topics)
