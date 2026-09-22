"""Offline regressions for the code generator's HTML and reference state."""

import json

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from scrapegraphai.graphs import CodeGeneratorGraph
from scrapegraphai.nodes import GenerateCodeNode


class Project(BaseModel):
    title: str
    description: str = ""


class Projects(BaseModel):
    projects: list[Project]


HTML = '<html><body><h1 class="project">First</h1></body></html>'
CODE = """def extract_data(html):
    soup = BeautifulSoup(html, "html.parser")
    return {"projects": [{"title": soup.select_one("h1.project").get_text(),
                          "description": ""}]}
"""


@pytest.mark.parametrize("list_reference", [False, True])
@pytest.mark.parametrize("source_kind", ["html", "url"])
@pytest.mark.parametrize("force", [False, True])
def test_run_preserves_html_for_analysis_and_execution(
    monkeypatch, tmp_path, source_kind, force, list_reference
):
    """Exercise run(), including real parsing and generated-code validation."""
    prompts = []
    projects = [{"title": "First", "description": ""}]
    reference = projects if list_reference else {"projects": projects}
    responses = iter(
        [
            json.dumps(reference),
            "Extract the project title.",
            "Project titles are in h1.project elements.",
            CODE,
            json.dumps(
                {
                    "are_semantically_equivalent": True,
                    "differences": [],
                    "explanation": "Same project.",
                }
            ),
        ]
    )

    def generate(self, messages, **kwargs):
        prompts.append(messages)
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=next(responses)))]
        )

    monkeypatch.setattr(ChatOpenAI, "_generate", generate)
    monkeypatch.setattr(
        "scrapegraphai.nodes.fetch_node.ChromiumLoader.load",
        lambda self: [Document(page_content=HTML)],
    )
    monkeypatch.setattr(
        "scrapegraphai.graphs.base_graph.log_graph_execution", lambda **kwargs: None
    )
    monkeypatch.chdir(tmp_path)
    graph = CodeGeneratorGraph(
        prompt="List the project titles and descriptions.",
        source=HTML if source_kind == "html" else "https://example.com/projects",
        config={
            "llm": {
                "model_instance": ChatOpenAI(model="gpt-4o-mini", api_key="test-key"),
                "model_tokens": 8192,
            },
            "force": force,
        },
        schema=Projects,
    )

    result = graph.run()

    assert result.strip() == CODE.strip()
    assert (tmp_path / "extracted_data.py").read_text() == result
    assert graph.final_state["doc"][0].page_content == HTML
    assert 'class="project"' in prompts[2][0].content
    assert len(prompts) == (5 if list_reference else 4)


@pytest.mark.parametrize(
    "reference",
    [
        {"projects": [{"title": "First"}, {"title": "Second"}]},
        [{"title": "First"}, {"title": "Second"}],
        {"items": [{"title": "First"}, {"title": "Second"}]},
    ],
    ids=["schema-valid-object", "list", "schema-invalid-object"],
)
def test_semantic_comparison_keeps_the_complete_reference(reference):
    """Validate conforming objects and send other JSON intact to comparison."""
    prompts = []
    comparison = {
        "are_semantically_equivalent": True,
        "differences": [],
        "explanation": "Both results contain the same two projects.",
    }

    def compare(prompt):
        prompts.append(prompt.to_string())
        return AIMessage(content=json.dumps(comparison))

    node = GenerateCodeNode(
        input="user_prompt & doc",
        output=["generated_code"],
        node_config={"llm_model": RunnableLambda(compare), "schema": Projects},
    )
    generated = {
        "projects": [
            {"title": "First", "description": ""},
            {"title": "Second", "description": ""},
        ]
    }

    result = node.semantic_comparison(generated, reference)

    assert result["are_semantically_equivalent"] is True
    if isinstance(reference, dict) and "projects" in reference:
        assert prompts == []
    else:
        assert len(prompts) == 1
        assert json.dumps(reference, indent=2) in prompts[0]
