"""
Parse_state_key test module 
"""
import pytest
from scrapegraphai.utils.parse_state_keys import parse_expression


def test_parse_expression():
    """Test parse_expression function."""
    EXPRESSION = "user_input & (relevant_chunks | parsed_document | document)"
    state = {
        "user_input": None,
        "document": None,
        "parsed_document": None,
        "relevant_chunks": None,
    }
    try:
        result = parse_expression(EXPRESSION, state)
        assert result != []
    except ValueError as e:
        assert "Error" in str(e)
