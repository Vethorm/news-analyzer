from news_helper.summarizer.utils import summarize_recursive
from loguru import logger


def summarize(text: str) -> str:
    try:
        summary = summarize_recursive(text)
        return summary
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return "Summary failed"
