def scrape_bill_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
    
    # Extract text - this will vary based on the page structure
    text_sections = []
    for section in soup.select('.field--name-body .field__item, .bill-section'):
        text_sections.append(section.get_text(strip=True))
    
    full_text = "\n\n".join(text_sections)
    
    return {
        "title": title,
        "text": full_text,
        "url": url
    }
