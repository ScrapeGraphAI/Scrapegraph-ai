import pytest

from scrapegraphai.nodes.base_node import BaseNode


class DummyNode(BaseNode):
    def execute(self, state):
        return state


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("a & (b & c)", ["a", "b", "c"]),
        ("(a & b) & c", ["a", "b", "c"]),
        ("(a & b) | c", ["a", "b"]),
        ("a & (d | b)", ["a", "b"]),
    ],
)
def test_get_input_keys_with_parentheses(expression, expected):
    node = DummyNode("Dummy", "node", expression, ["out"])
    state = {"a": 1, "b": 2, "c": 3}

    assert node.get_input_keys(state) == expected
