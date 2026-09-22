"""Offline regressions for the code generator's HTML and reference state."""

import json

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from scrapegraphai.graphs import CodeGeneratorGraph


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


@pytest.mark.parametrize("source_kind", ["html", "url"])
@pytest.mark.parametrize("force", [False, True])
def test_run_preserves_html_for_analysis_and_execution(
    monkeypatch, tmp_path, source_kind, force
):
    """Exercise run(), including real parsing and generated-code validation."""
    prompts = []
    responses = iter(
        [
            json.dumps({"projects": [{"title": "First", "description": ""}]}),
            "Extract the project title.",
            "Project titles are in h1.project elements.",
            CODE,
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
    assert len(prompts) == 4
