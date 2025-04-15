import pytest

from scrapegraphai.nodes.base_node import BaseNode


class DummyNode(BaseNode):
    """Dummy node for testing BaseNode methods."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, state: dict) -> dict:
        """Simple execute implementation that returns the state unchanged."""
        return state


# A constant representing a dummy state for testing input keys
TEST_STATE = {"a": 1, "b": 2, "c": 3}


class TestBaseNode:
    """Test suite for BaseNode functionality."""

    def setup_method(self):
        """Setup DummyNode instance for tests."""
        self.node = DummyNode(
            node_name="TestNode",
            node_type="node",
            input="a",
            output=["x"],
            min_input_len=1,
        )

    def test_execute_returns_state(self):
        """Test if execute method returns state unchanged."""
        state = {"a": 10}
        updated = self.node.execute(state)
        assert updated == state

    def test_invalid_node_type(self):
        """Test that an invalid node_type raises ValueError."""
        with pytest.raises(ValueError):
            DummyNode(
                node_name="InvalidNode", node_type="invalid", input="a", output=["x"]
            )

    def test_update_config_without_overwrite(self):
        """Test update_config does not overwrite existing attributes when overwrite is False."""
        original_input = self.node.input
        self.node.update_config({"input": "new_input"})
        assert self.node.input == original_input

    def test_update_config_with_overwrite(self):
        """Test update_config updates attributes when overwrite is True."""
        self.node.update_config({"input": "new_input_value"}, overwrite=True)
        assert self.node.input == "new_input_value"

    @pytest.mark.parametrize(
        "expression, expected",
        [
            ("a", ["a"]),
            ("a|b", ["a"]),
            ("a&b", ["a", "b"]),
            (
                "(a&b)|c",
                ["a", "b"],
            ),  # Since a and b are valid, returns the first matching OR segment.
            (
                "a&(b|c)",
                ["a", "b"],
            ),  # Evaluation returns the first matching AND condition.
        ],
    )
    def test_get_input_keys_valid(self, expression, expected):
        """Test get_input_keys returns correct keys for valid expressions."""
        self.node.input = expression
        result = self.node.get_input_keys(TEST_STATE)
        # Check that both sets are equal, ignoring order.
        assert set(result) == set(expected)

    @pytest.mark.parametrize(
        "expression",
        [
            "",  # empty expression should raise an error
            "a||b",  # consecutive operator ||
            "a&&b",  # consecutive operator &&
            "a b",  # adjacent keys without operator should be caught by regex
            "(a&b",  # missing a closing parenthesis
            "a&b)",  # extra closing parenthesis
            "&a",  # invalid start operator
            "a|",  # invalid end operator
            "a&|b",  # invalid operator order
        ],
    )
    def test_get_input_keys_invalid(self, expression):
        """Test get_input_keys raises ValueError for invalid expressions."""
        self.node.input = expression
        with pytest.raises(ValueError):
            self.node.get_input_keys(TEST_STATE)

    def test_validate_input_keys_insufficient_keys(self):
        """Test that _validate_input_keys raises an error if the returned input keys are insufficient."""
        self.node.min_input_len = 2
        # Use an expression that returns only one key
        self.node.input = "a"
        with pytest.raises(ValueError):
            self.node.get_input_keys(TEST_STATE)

    def test_nested_parentheses(self):
        """Test get_input_keys correctly parses nested parentheses in expressions."""
        # Expression with nested parentheses; expected to yield keys "a" and "b"
        self.node.input = "((a)&(b|c))"
        result = self.node.get_input_keys(TEST_STATE)
        assert set(result) == {"a", "b"}

    def test_execute_integration_with_state(self):
        """Integration test: Pass a non-trivial state to execute and ensure output matches."""
        state = {"a": 100, "b": 200, "c": 300}
        result = self.node.execute(state)
        assert result == state

    # End of tests
