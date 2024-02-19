"""
Example for calclating the tokenizer
"""
from scrapegraphai.utils.token_calculator import truncate_text_tokens

INPUT_TEXT = "http://nba.com"

MODEL_NAME = "gpt-3.5-turbo"
ENCODING_NAME = "EMBEDDING_ENCODING"

tokenized_chunks = truncate_text_tokens(INPUT_TEXT, MODEL_NAME, ENCODING_NAME)

for i, chunk in enumerate(tokenized_chunks):
    print(f"Chunk {i+1}: {chunk}")
