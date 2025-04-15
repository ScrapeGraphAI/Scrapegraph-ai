from pydantic import BaseModel

from scrapegraphai.graphs.base_graph import BaseGraph
from scrapegraphai.graphs.smart_scraper_multi_graph import SmartScraperMultiGraph


# Dummy classes to simulate graph execution
class DummyGraph:
    """Dummy graph that always returns an answer."""

    def execute(self, inputs):
        return {"answer": "Test answer"}, "dummy execution info"


class DummyGraphNoAnswer:
    """Dummy graph that returns no answer key."""

    def execute(self, inputs):
        return {"not_answer": "missing"}, "dummy execution info"


class DummyGraphRecord:
    """Dummy graph that records the input provided to execute()."""

    def __init__(self):
        self.last_inputs = None

    def execute(self, inputs):
        self.last_inputs = inputs
        return {"answer": "Recorded Answer"}, "dummy execution info"


class DummySchema(BaseModel):
    answer: str


# Tests for SmartScraperMultiGraph
def test_run_returns_answer():
    """
    Test that run() returns the answer provided by the dummy graph.
    """
    config = {"llm": {"model": "dummy"}}
    scraper = SmartScraperMultiGraph(
        prompt="Test prompt", source=["http://example.com"], config=config
    )
    scraper.graph = DummyGraph()
    scraper.llm_model = {"model": "dummy"}
    result = scraper.run()
    assert result == "Test answer"


def test_run_no_answer_found():
    """
    Test that run() returns 'No answer found.' when the dummy graph does not provide an answer.
    """
    config = {"llm": {"model": "dummy"}}
    scraper = SmartScraperMultiGraph(
        prompt="Another test", source=["http://example.org"], config=config
    )
    scraper.graph = DummyGraphNoAnswer()
    scraper.llm_model = {"model": "dummy"}
    result = scraper.run()
    assert result == "No answer found."


def test_create_graph_structure():
    """
    Test that _create_graph() returns a valid BaseGraph with two nodes and one edge.
    """
    config = {"llm": {"model": "dummy"}}
    scraper = SmartScraperMultiGraph(
        prompt="Graph test", source=["http://example.net"], config=config
    )
    scraper.llm_model = {"model": "dummy"}
    graph = scraper._create_graph()
    assert isinstance(graph, BaseGraph)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1


def test_run_records_proper_input():
    """
    Test that run() sends the correct input to the graph's execute method.
    """
    config = {"llm": {"model": "dummy"}}
    scraper = SmartScraperMultiGraph(
        prompt="Record input", source=["http://recorder.com"], config=config
    )
    dummy_record = DummyGraphRecord()
    scraper.graph = dummy_record
    scraper.llm_model = {"model": "dummy"}
    scraper.run()
    expected_inputs = {"user_prompt": "Record input", "urls": ["http://recorder.com"]}
    assert dummy_record.last_inputs == expected_inputs
