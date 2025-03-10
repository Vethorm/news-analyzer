import pandas as pd

import streamlit as st
from news_helper.articles.apnews import extract_article_text, get_recent_articles
from news_helper.entity import extract_entities
from news_helper.summarizer import summarize

st.title("New Analyzer")

articles = get_recent_articles()
articles = {article["title"]: article for article in articles}


selected_article = st.selectbox("Pick an article", list(articles.keys()))

if selected_article:
    st.header(selected_article)

    article = articles[selected_article]
    st.page_link(article["url"], label="Article link")

    with st.spinner("Summarizing article...") as s:
        article_text = extract_article_text(article["url"])
        article_summary = summarize(article_text)
    article_compression = (1 - (len(article_summary) / len(article_text))) * 100
    st.write(f"Article compression: {article_compression:.2f}%")
    st.write(article_summary)

    st.subheader("Extracted Entities")
    with st.spinner("Extracting entities...") as s:
        # Run the entity extraction on the summarized text (or article_text if preferred)
        entities = extract_entities(article_text)
    if entities:
        # Convert the list of entity dictionaries into a Pandas DataFrame for a nice display.
        entities_df = pd.DataFrame(entities)
        st.dataframe(entities_df)
    else:
        st.write("No entities found.")
