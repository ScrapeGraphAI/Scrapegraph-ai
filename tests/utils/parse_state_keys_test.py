"""
Parse_state_key test module
"""

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


def test_parse_expression_and_inside_parentheses():
    """Every key of an AND group in parentheses is required and returned."""
    state = {"a": None, "b": None, "c": None}

    assert parse_expression("a & (b & c)", state) == ["a", "b", "c"]
    assert parse_expression("(a & b) & c", state) == ["a", "b", "c"]
    assert parse_expression("(a & b) | c", state) == ["a", "b"]
