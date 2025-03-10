from news_helper.entity.utils import get_entities


def extract_entities(text: str) -> dict:
    return get_entities(text)
