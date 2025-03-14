# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 17:55:45 2025

@author: MUSTAFA
"""
import requests
import streamlit as st

class NewsSummarizer:
    def __init__(self, api_key, openrouter_api_key):
        self.api_key = api_key
        self.openrouter_api_key = openrouter_api_key

    def translate_text(self, text, target_language):
        api_url = 'https://openrouter.ai/api/v1/chat/completions'
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "google/gemma-3-27b-it:free",
            "messages": [
                {"role": "user", "content": f"Translate the entire text into {target_language}. No extra explanations.: {text}"}
            ],
            "max_tokens": 5000
        }
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        else:
            return None

    def get_news(self, interest, news_number=3, target_language='none', from_date=None, to_date=None):
        url = f"https://newsapi.org/v2/everything?q={interest}&apiKey={self.api_key}"
        if from_date and to_date:
            if from_date > to_date:
                st.error('End date must be after start date.')
                return
            url += f"&from={from_date}&to={to_date}"

        response = requests.get(url)
        data = response.json()

        if data.get('status') == 'ok':
            articles = data.get('articles', [])[:news_number]
            for i, article in enumerate(articles, 1):
                st.write(f"**{i}. {article.get('title', 'No Title')}**")
                st.write(f"Source: {article.get('source', {}).get('name', 'Unknown')}")
                st.write(f"URL: {article.get('url', 'No URL')}")
                
                # Show image if available
                content = article.get('content', '')
                if content:
                    summary = self.summary_text(content, target_language)
                    st.write(f"Summary: {summary}\n")
                    image_url = article.get('urlToImage', None)
                    if image_url:
                        st.image(image_url, width=400)
                else:
                    st.write("News content not found.\n")
        else:
            st.write("Something went wrong getting news.")

    def summary_text(self, text, target_language):
        api_url = 'https://openrouter.ai/api/v1/chat/completions'
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek/deepseek-r1-zero:free",
            "messages": [
                {"role": "user", "content": f"Summarize the news: {text}"}
            ],
            "max_tokens": 4000
        }
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            if content:
                if target_language == 'none':
                    return content
                else:
                    return self.translate_text(content, target_language)
            else:
                payload = {
                    "model": "qwen/qwq-32b:free",
                    "messages": [
                        {"role": "user", "content": f"Summarize the news: {text}"}
                    ],
                    "max_tokens": 8000
                }
                response = requests.post(api_url, headers=headers, json=payload)
                if response.status_code == 200:
                    content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                    if content:
                        if target_language == 'none':
                            return content
                        else:
                            return self.translate_text(content, target_language)
                    else:
                        return 'Something went wrong while summarizing.'
                else:
                    return str(response.json())
        else:
            return str(response.json())

def main():
    st.title("News Summarizer")

    # Sidebar inputs
    api_key = st.secrets["NEWS_API_KEY"]
    openrouter_api_key = st.secrets["OPENROUTER_API_KEY"]
    news_summarizer = NewsSummarizer(api_key, openrouter_api_key)

    interest = st.sidebar.text_input("Enter your area of interest:")
    news_number = st.sidebar.number_input("Write how many news you want to see:", min_value=1, value=3)
    target_language = st.sidebar.selectbox('Please select the news language', ['English', 'German', 'Italian', 'French', 'Chinese', 'Turkish'])
    from_date = st.sidebar.date_input('Start Date:', value=None)
    to_date = st.sidebar.date_input('End Date:', value=None)

    if st.sidebar.button("Get News"):
        if from_date and to_date and from_date > to_date:
            st.error('End date must be after start date.')
        else:
            with st.spinner("Getting news..."):
                news_summarizer.get_news(interest, news_number, target_language, from_date, to_date)

if __name__ == "__main__":
    main()
