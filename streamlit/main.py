import streamlit as st
from news_helper.articles.apnews import extract_article_text, get_recent_articles
from news_helper.summarizer import summarize

st.title("New Analyzer")

articles = get_recent_articles()
articles = {article["title"]: article for article in articles}


selected_article = st.selectbox("Pick an article", list(articles.keys()))

if selected_article:
    st.header(selected_article)

    article = articles[selected_article]
    st.page_link(article["url"], label="Article link")

    # with st.spinner("Summarizing article...") as s:
    article_text = extract_article_text(article["url"])
    article_summary = summarize(article_text)
    st.write(article_summary)
