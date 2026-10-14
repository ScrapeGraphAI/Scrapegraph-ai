import pytest
from langchain_core.prompts import PromptTemplate
from scrapegraphai import prompts


@pytest.mark.parametrize(
    "template_name",
    ["TEMPLATE_CHUNKS_MD", "TEMPLATE_CHUNKS"],
)
def test_chunk_prompts_include_user_question(template_name):
    """Ensure each chunk receives the user's extraction question."""
    from langchain_core.prompts import PromptTemplate
    from scrapegraphai import prompts

    template = getattr(prompts, template_name)

    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={
            "content": "Django and Flask are Python web frameworks.",
            "chunk_id": 1,
            "format_instructions": "Return valid JSON.",
        },
    )

    rendered = prompt.format(question="Which Python frameworks are mentioned?")

    assert "USER QUESTION: Which Python frameworks are mentioned?" in rendered
    assert "Django and Flask" in rendered


def test_k_level_chunk_receives_question(monkeypatch):
    """Verify K-level chunk processing includes the question and JSON instructions."""
    from langchain_core.runnables import RunnableLambda
    from scrapegraphai.nodes.generate_answer_node_k_level import GenerateAnswerNodeKLevel

    captured_prompts = []

    def fake_llm(prompt):
        captured_prompts.append(prompt.to_string())
        return '{"content": "Django"}'

    class FakeResult:
        id = 1
        score = 0.9

    class FakeDB:
        def query(self, collection_name, query_text):
            return [FakeResult()]

    node = GenerateAnswerNodeKLevel(
        "user_prompt & docs & vectorial_db",
        ["answer"],
        node_config={"llm_model": RunnableLambda(fake_llm), "verbose": False},
    )

    node.execute({
        "user_prompt": "Which Python frameworks are mentioned?",
        "docs": [{"document": "Django is a Python framework."}],
        "vectorial_db": FakeDB(),
    })

    assert captured_prompts
    assert "USER QUESTION: Which Python frameworks are mentioned?" in captured_prompts[0]
    assert "OUTPUT INSTRUCTIONS:" in captured_prompts[0]
    assert "OUTPUT INSTRUCTIONS: Return a JSON object." in captured_prompts[0]
