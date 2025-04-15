import pytest

from scrapegraphai.nodes.concat_answers_node import ConcatAnswersNode


class DummyBaseNode:
    """Dummy class to simulate BaseNode's get_input_keys method for testing."""

    def get_input_keys(self, state: dict):
        # For testing, assume self.input is a single key or a comma-separated list of keys.
        if "," in self.input:
            return [key.strip() for key in self.input.split(",")]
        else:
            return [self.input]


# Monkey-patch ConcatAnswersNode to use DummyBaseNode's get_input_keys method.
ConcatAnswersNode.get_input_keys = DummyBaseNode.get_input_keys


class TestConcatAnswersNode:
    """Test suite for the ConcatAnswersNode functionality."""

    def test_execute_multiple_answers(self):
        """Test execute with multiple answers concatenated into a merged dictionary."""
        node = ConcatAnswersNode(
            input="answers", output=["result"], node_config={"verbose": True}
        )
        state = {"answers": ["Answer one", "Answer two", "Answer three"]}
        updated_state = node.execute(state)
        expected = {
            "products": {
                "item_1": "Answer one",
                "item_2": "Answer two",
                "item_3": "Answer three",
            }
        }
        assert updated_state["result"] == expected

    def test_execute_single_answer(self):
        """Test execute with a single answer returns the answer directly."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        state = {"answers": ["Only answer"]}
        updated_state = node.execute(state)
        assert updated_state["result"] == "Only answer"

    def test_execute_missing_input_key_raises_keyerror(self):
        """Test execute raises KeyError when the required input key is missing in the state."""
        node = ConcatAnswersNode(input="missing_key", output=["result"])
        state = {"some_other_key": "data"}
        with pytest.raises(KeyError):
            node.execute(state)

    def test_merge_dict_private_method(self):
        """Test the _merge_dict private method to ensure correct merge of a list of answers."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        data = ["A", "B"]
        merged = node._merge_dict(data)
        expected = {"products": {"item_1": "A", "item_2": "B"}}
        assert merged == expected

    def test_verbose_flag(self):
        """Test that node initialization with verbose flag does not interfere with execute."""
        node = ConcatAnswersNode(
            input="answers", output=["result"], node_config={"verbose": True}
        )
        state = {"answers": ["Verbose answer"]}
        updated_state = node.execute(state)
        # When only one answer is provided, the answer should be returned directly.
        assert updated_state["result"] == "Verbose answer"

    def test_merge_dict_empty(self):
        """Test _merge_dict with an empty list returns an empty products dictionary."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        merged = node._merge_dict([])
        expected = {"products": {}}
        assert merged == expected

    def test_execute_empty_answers(self):
        """Test execute raises an IndexError when the 'answers' list is empty."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        state = {"answers": []}
        with pytest.raises(IndexError):
            node.execute(state)

    def test_execute_comma_separated_input(self):
        """Test execute with comma-separated input keys returns correct result using first key."""
        node = ConcatAnswersNode(input="answers, extra", output=["result"])
        state = {"answers": ["First answer", "Second answer"], "extra": "dummy"}
        updated_state = node.execute(state)
        # Since "answers" list has length > 1, expected merged dictionary.
        expected = {"products": {"item_1": "First answer", "item_2": "Second answer"}}
        assert updated_state["result"] == expected

    def test_verbose_logging(self):
        """Test that verbose mode triggers logging of the execution start message."""
        node = ConcatAnswersNode(
            input="answers", output=["result"], node_config={"verbose": True}
        )
        # Setup a dummy logger to capture log messages.
        logged_messages = []
        node.logger = type(
            "DummyLogger", (), {"info": lambda self, msg: logged_messages.append(msg)}
        )()
        state = {"answers": ["Only answer"]}
        node.execute(state)
        # Check that one of the logged messages includes 'Executing ConcatAnswers'
        assert any("Executing ConcatAnswers" in message for message in logged_messages)

    def test_execute_tuple_input(self):
        """Test execute with tuple input for answers returns a merged dictionary."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        state = {"answers": ("first", "second")}
        updated_state = node.execute(state)
        expected = {"products": {"item_1": "first", "item_2": "second"}}
        assert updated_state["result"] == expected

    def test_execute_string_input(self):
        """Test execute with a string input for answers returns a merged dictionary by iterating each character."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        state = {"answers": "hello"}
        updated_state = node.execute(state)
        expected = {
            "products": {
                "item_1": "h",
                "item_2": "e",
                "item_3": "l",
                "item_4": "l",
                "item_5": "o",
            }
        }
        assert updated_state["result"] == expected

    def test_execute_non_iterable_input_raises_error(self):
        """Test execute with a non-iterable input for answers raises a TypeError."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        state = {"answers": 123}
        with pytest.raises(TypeError):
            node.execute(state)

    def test_execute_dict_input(self):
        """Test execute with dict input for answers. Since iterating over a dict yields its keys,
        the merged dictionary should consist of the dict keys."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        state = {"answers": {"k1": "Answer one", "k2": "Answer two"}}
        updated_state = node.execute(state)
        expected = {"products": {"item_1": "k1", "item_2": "k2"}}
        assert updated_state["result"] == expected

    def test_execute_generator_input(self):
        """Test execute with a generator input for answers raises a TypeError because generators do
        not support len() calls."""
        node = ConcatAnswersNode(input="answers", output=["result"])
        state = {"answers": (x for x in ["A", "B"])}
        with pytest.raises(TypeError):
            node.execute(state)
