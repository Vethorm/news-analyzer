from transformers import pipeline
from transformers import logging as transformers_logging

transformers_logging.set_verbosity_error()

import torch
from loguru import logger


torch.classes.__path__ = []  # https://github.com/VikParuchuri/marker/issues/442#issuecomment-2636393925


if torch.cuda.is_available():
    logger.info("Number of GPUs available:", torch.cuda.device_count())
    for i in range(torch.cuda.device_count()):
        logger.info(f"GPU {i}: {torch.cuda.get_device_name(i)}")
else:
    logger.info("CUDA is not available. Using CPU.")

device = "cpu"  # force to CPU, getting weird issues on laptop GPU


class SummarizationModels:
    PEGASUS_XSUM: str = "google/pegasus-xsum"
    PEGASUS_LARGE: str = "google/pegasus-large"
    BART_LARGE_CNN: str = "facebook/bart-large-cnn"


summarizer = pipeline("summarization", model=SummarizationModels.PEGASUS_XSUM, device=-1)  # Use CPU explicitlyz


def chunk_text(text: str, max_tokens: int = 900) -> list:
    sentences = text.split(". ")
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if len((current_chunk + sentence).split()) <= max_tokens:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    logger.info(f"Chunk counts and lengths: {[len(chunk.split()) for chunk in chunks]}")
    return chunks


def summarize_recursive(
    text: str, target_length: int = 150, model: str = SummarizationModels.PEGASUS_XSUM, max_iterations: int = 5
) -> str:
    """
    Summarizes text recursively to achieve a target length.

    Args:
        text (str): Input text to summarize.
        target_length (int): Desired length for the final summary.
        model (str): Pretrained model for summarization.
        max_iterations (int): Maximum number of iterations for recursive summarization.

    Returns:
        str: The summarized text.

    Raises:
        ValueError: If input text is empty or too short.
        RuntimeError: If summarization fails to achieve target length after max_iterations.
    """
    # Validate input
    if not text.strip():
        raise ValueError("text cannot be empty or whitespace.")
    if len(text.split()) < 10:
        raise ValueError("Input text must contain at least 10 words.")

    logger.info("Splitting text into manageable chunks...")
    text_chunks = chunk_text(text, 150)[:1]
    logger.info(f"Number of chunks created: {len(text_chunks)}")

    summaries = []
    for chunk in text_chunks:
        try:
            summary = summarizer(chunk, min_length=10, max_length=150)[0]["summary_text"]
            summaries.append(summary)
        except Exception as e:
            logger.warning(f"Failed to summarize chunk: {e}")
            summaries.append("")  # Append an empty summary for failed chunks

    combined_summary = " ".join(summaries)
    logger.info(f"Initial combined summary length: {len(combined_summary.split())} words")

    iteration = 0
    while len(combined_summary.split()) > target_length and iteration < max_iterations:
        try:
            logger.info(f"Iteration {iteration + 1}: Refining summary...")
            combined_summary = summarizer(combined_summary, min_length=30, max_length=target_length)[0]["summary_text"]
            logger.info(f"New summary length: {len(combined_summary.split())} words")
        except Exception as e:
            logger.warning(f"Failed to refine the summary at iteration {iteration + 1}: {e}")
            break
        iteration += 1

    if iteration == max_iterations:
        logger.warning("Maximum iterations reached. Final summary may exceed the target length.")

    return combined_summary
