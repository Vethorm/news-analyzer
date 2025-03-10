from gliner import GLiNER
from loguru import logger


class GlinerModels:
    LARGE_NEWS = "EmergentMethods/gliner_large_news-v2.1"
    LARGE_V2 = "urchade/gliner_large-v2"


entity_extractor = GLiNER.from_pretrained(GlinerModels.LARGE_NEWS)
labels = ["company"]


def get_entities(text):
    """
    Predict entities in the given text using GLiNER and return unique entities
    with their corresponding label and confidence score.

    Parameters:
        text (str): The input text to analyze.

    Returns:
        list: A list of dictionaries, each representing a unique predicted entity,
              with keys "entity", "label", and "score".
    """
    # Split text into sentences using periods.
    sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
    logger.info(f"Extracting entities from {len(sentences)} sentences")
    unique_entities = {}
    for sentence in sentences:
        entities = entity_extractor.predict_entities(sentence, labels)
        for entity in entities:
            ent_text = entity.get("text")
            ent_label = entity.get("label")
            ent_score = entity.get("score")
            # If the entity has already been seen, update only if the new score is higher.
            if ent_text in unique_entities:
                if ent_score > unique_entities[ent_text]["label_data"]["score"]:
                    unique_entities[ent_text]["label_data"] = {"label": ent_label, "score": ent_score}
            else:
                unique_entities[ent_text] = {"label_data": {"label": ent_label, "score": ent_score}}

    # Convert the aggregated dictionary into a list for the UI.
    output = [
        {"entity": ent_text, "label": data["label_data"]["label"], "score": data["label_data"]["score"]}
        for ent_text, data in unique_entities.items()
    ]
    logger.info("Done extracting")
    return output
