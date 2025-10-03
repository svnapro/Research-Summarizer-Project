import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.title("Research Paper Summarizer")

def summarize_text(text, num_sentences=3):
    sentences = text.split('. ')
    if len(sentences) <= num_sentences:
        return text
    
    words = text.lower().split()
    word_freq = {}
    for word in words:
        word = word.strip('.,!?;:')
        if len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        score = 0
        sentence_words = sentence.lower().split()
        for word in sentence_words:
            word = word.strip('.,!?;:')
            if word in word_freq:
                score += word_freq[word]
        sentence_scores[i] = score
    
    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    top_indices.sort()
    
    summary = '. '.join([sentences[i] for i in top_indices])
    if not summary.endswith('.'):
        summary += '.'
    
    return summary

topic = st.text_input("Enter a research topic:")

if st.button("Fetch Papers") and topic:
    with st.spinner("Fetching papers..."):
        search_url = f"https://arxiv.org/search/?query={topic}&searchtype=all&source=header"
        try:
            response = requests.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            papers = soup.find_all('li', class_='arxiv-result')[:3]
            
            if not papers:
                st.error("No papers found for this topic.")
            else:
                for i, paper in enumerate(papers, 1):
                    title_elem = paper.find('p', class_='title')
                    abstract_elem = paper.find('span', class_='abstract-full')
                    
                    if not abstract_elem:
                        abstract_elem = paper.find('p', class_='abstract')
                    
                    title = title_elem.get_text(strip=True) if title_elem else "Title not found"
                    abstract = abstract_elem.get_text(strip=True) if abstract_elem else "Abstract not found"
                    
                    title = re.sub(r'\s+', ' ', title)
                    abstract = re.sub(r'\s+', ' ', abstract)
                    
                    summary = summarize_text(abstract, num_sentences=3)
                    
                    st.subheader(f"Paper {i}")
                    st.write(f"**Title:** {title}")
                    st.write(f"**Summary:** {summary}")
                    st.divider()
                    
        except Exception as e:
            st.error(f"Error fetching papers: {str(e)}")