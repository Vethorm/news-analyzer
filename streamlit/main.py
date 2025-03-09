import streamlit as st
from news_helper.articles.apnews import get_recent_articles, extract_article_text
from news_helper.summarizer import summarize

st.title("New Analyzer")

articles = get_recent_articles()
articles = {article["title"]: article for article in articles}


selected_article = st.selectbox("Pick an article", list(articles.keys()))

if selected_article:
    st.header(selected_article)

    # with st.spinner("Summarizing article...") as s:
    article_text = extract_article_text(articles[selected_article]["url"])
    article_summary = summarize(article_text)
    st.write(article_summary)
