from loguru import logger

from news_helper.summarizer.utils import summarize_recursive


def summarize(text: str) -> str:
    try:
        summary = summarize_recursive(text)
        return summary
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return "Summary failed"
