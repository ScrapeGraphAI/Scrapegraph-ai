"""
Tests for the silent-error-page guards added for issue #1102.

Two independent signals are covered:

1. ``ChromiumLoader`` warns when ``page.goto()`` reports an HTTP error status,
   so a 404/403/500 page is no longer handed to the LLM as if it were the
   intended document.
2. ``ParseNode`` warns when the parsed content contains no trace of what the
   user asked for, which also catches 200 pages whose content never rendered.
"""

import asyncio
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document
from pydantic import BaseModel

from scrapegraphai.docloaders.chromium import ChromiumLoader, _warn_on_error_status
from scrapegraphai.nodes import ParseNode
from scrapegraphai.utils.logging import set_propagation, unset_propagation

# --------------------------------------------------------------------------- #
# ChromiumLoader: HTTP status awareness on every page.goto() call site
# --------------------------------------------------------------------------- #


class _MockPage:
    def __init__(self, status):
        response = MagicMock()
        response.status = status
        self.goto = AsyncMock(return_value=response)
        self.wait_for_load_state = AsyncMock()
        self.content = AsyncMock(return_value="<html>error page</html>")
        self.evaluate = AsyncMock(return_value=1000)
        self.mouse = MagicMock()
        self.mouse.wheel = AsyncMock()


@pytest.fixture
def playwright_with_status():
    """Patch playwright so page.goto() returns a response with a given status."""

    def _factory(status):
        page = _MockPage(status)
        context = MagicMock()
        context.new_page = AsyncMock(return_value=page)
        browser = MagicMock()
        browser.new_context = AsyncMock(return_value=context)
        browser.close = AsyncMock()
        pw = MagicMock()
        pw.chromium.launch = AsyncMock(return_value=browser)
        pw.firefox.launch = AsyncMock(return_value=browser)

        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=pw)
        cm.__aexit__ = AsyncMock(return_value=False)
        return cm, page

    return _factory


@pytest.mark.parametrize("status", [404, 403, 500, 503])
def test_ascrape_playwright_warns_on_error_status(
    playwright_with_status, status, caplog
):
    cm, _ = playwright_with_status(status)
    loader = ChromiumLoader(["https://example.com/missing"], backend="playwright")

    with (
        patch("playwright.async_api.async_playwright", return_value=cm),
        patch("undetected_playwright.Malenia.apply_stealth", new=AsyncMock()),
        caplog.at_level("WARNING"),
    ):
        asyncio.run(loader.ascrape_playwright("https://example.com/missing"))

    assert f"Received HTTP {status}" in caplog.text
    assert "likely an error page" in caplog.text


def test_ascrape_playwright_silent_on_success(playwright_with_status, caplog):
    cm, _ = playwright_with_status(200)
    loader = ChromiumLoader(["https://example.com"], backend="playwright")

    with (
        patch("playwright.async_api.async_playwright", return_value=cm),
        patch("undetected_playwright.Malenia.apply_stealth", new=AsyncMock()),
        caplog.at_level("WARNING"),
    ):
        asyncio.run(loader.ascrape_playwright("https://example.com"))

    assert "Received HTTP" not in caplog.text


def test_ascrape_with_js_support_warns_on_error_status(playwright_with_status, caplog):
    cm, _ = playwright_with_status(404)
    loader = ChromiumLoader(
        ["https://example.com/missing"], backend="playwright", requires_js_support=True
    )

    with (
        patch("playwright.async_api.async_playwright", return_value=cm),
        caplog.at_level("WARNING"),
    ):
        asyncio.run(loader.ascrape_with_js_support("https://example.com/missing"))

    assert "Received HTTP 404" in caplog.text


def test_ascrape_playwright_scroll_warns_on_error_status(
    playwright_with_status, caplog
):
    cm, page = playwright_with_status(404)
    # Stop the scroll loop immediately: same height twice means "bottom reached".
    page.evaluate = AsyncMock(return_value=1000)
    loader = ChromiumLoader(["https://example.com/missing"], backend="playwright")

    with (
        patch("playwright.async_api.async_playwright", return_value=cm),
        patch("undetected_playwright.Malenia.apply_stealth", new=AsyncMock()),
        caplog.at_level("WARNING"),
    ):
        asyncio.run(
            loader.ascrape_playwright_scroll(
                "https://example.com/missing", scroll=5000, sleep=0.01, timeout=1
            )
        )

    assert "Received HTTP 404" in caplog.text


def test_warn_on_error_status_tolerates_missing_response(caplog):
    """page.goto() returns None for same-document navigations; that is not an error."""
    with caplog.at_level("WARNING"):
        _warn_on_error_status(None, "https://example.com")
        _warn_on_error_status(MagicMock(status=None), "https://example.com")

    assert "Received HTTP" not in caplog.text


# --------------------------------------------------------------------------- #
# ParseNode: warn when the parsed content holds no trace of the request
# --------------------------------------------------------------------------- #


@pytest.fixture
def library_logs_propagate():
    """Let caplog see records from the library root logger.

    ``scrapegraphai`` disables propagation by default so it does not pollute the
    host application's logging; the nodes log through that root logger.
    """
    set_propagation()
    yield
    unset_propagation()


class Company(BaseModel):
    company_name: str
    foundingYear: int


class Employee(BaseModel):
    employee_name: str
    salary: str


class Payroll(BaseModel):
    employees: List[Employee]


def _parse_node(**node_config):
    config = {"chunk_size": 4096, "verbose": False}
    config.update(node_config)
    return ParseNode(input="doc", output=["parsed_doc"], node_config=config)


def _run(node, html, user_prompt):
    state = {"doc": [Document(page_content=html)], "user_prompt": user_prompt}
    return node.execute(state)


WIKIPEDIA_404 = (
    "<html><body><p>Jump to content. Main menu. Navigation. "
    "Wikipedia does not have an article with this exact name.</p></body></html>"
)

TIMPSON_PAGE = (
    "<html><body><p>Timpson is a British retailer founded in 1865 "
    "by William Timpson.</p></body></html>"
)

# A shell page whose real content is rendered client-side: HTTP 200, no error,
# and nothing for the LLM to work with.
JS_SHELL_PAGE = "<html><body><div id='root'>Loading...</div></body></html>"

STRUCTURED_PAGE = (
    "<html><body><p>Company name: Timpson</p>"
    "<p>Founding year: 1865</p></body></html>"
)


def test_warns_when_no_requested_term_is_present(library_logs_propagate, caplog):
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, WIKIPEDIA_404, "What is the founding year of Timpson?")

    assert "None of the requested terms" in caplog.text


def test_silent_when_the_content_holds_the_answer(library_logs_propagate, caplog):
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, TIMPSON_PAGE, "What is the founding year of Timpson?")

    assert "None of the requested terms" not in caplog.text


def test_schema_field_names_count_as_requested_terms(library_logs_propagate, caplog):
    """A page that never rendered is a 200, so only the schema can flag it."""
    node = _parse_node(schema=Company)

    with caplog.at_level("WARNING"):
        _run(node, JS_SHELL_PAGE, None)

    assert "None of the requested terms" in caplog.text
    # snake_case and camelCase names are split into their parts
    assert "founding" in caplog.text
    assert "company" in caplog.text
    assert "year" in caplog.text


def test_schema_match_keeps_the_check_quiet(library_logs_propagate, caplog):
    node = _parse_node(schema=Company)

    with caplog.at_level("WARNING"):
        _run(node, STRUCTURED_PAGE, None)

    assert "None of the requested terms" not in caplog.text


def test_schema_terms_can_rescue_an_unspecific_prompt(library_logs_propagate, caplog):
    """The union of prompt and schema terms only ever makes the check quieter."""
    node = _parse_node(schema=Company)

    with caplog.at_level("WARNING"):
        _run(node, STRUCTURED_PAGE, "Extract everything you can find")

    assert "None of the requested terms" not in caplog.text


def test_nested_pydantic_models_are_unwrapped(library_logs_propagate, caplog):
    """List[Item] and friends must not hide the nested field names."""
    node = _parse_node(schema=Payroll)

    with caplog.at_level("WARNING"):
        _run(node, JS_SHELL_PAGE, None)

    assert "salary" in caplog.text
    assert "employee" in caplog.text


def test_json_schema_dict_is_supported(library_logs_propagate, caplog):
    schema = {
        "type": "object",
        "properties": {
            "founding_year": {"type": "integer"},
            "locations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"postcode": {"type": "string"}},
                },
            },
        },
    }
    node = _parse_node(schema=schema)

    with caplog.at_level("WARNING"):
        _run(node, JS_SHELL_PAGE, None)

    assert "postcode" in caplog.text
    assert "locations" in caplog.text


def test_no_prompt_and_no_schema_produces_no_warning(library_logs_propagate, caplog):
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, WIKIPEDIA_404, None)

    assert "None of the requested terms" not in caplog.text


def test_generic_prompt_words_alone_do_not_trigger_the_warning(
    library_logs_propagate, caplog
):
    """A prompt made only of scraping vocabulary carries no signal to check."""
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, WIKIPEDIA_404, "Extract all the information from this webpage")

    assert "None of the requested terms" not in caplog.text


def test_empty_parsed_content_is_reported(library_logs_propagate, caplog):
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, "", "What is the founding year of Timpson?")

    assert "parsed content is empty" in caplog.text


def test_state_is_unchanged_by_the_guard():
    """The guard only logs; the parsed chunks must reach the state as before."""
    node = _parse_node(schema=Company)
    state = _run(node, TIMPSON_PAGE, "What is the founding year of Timpson?")

    assert state["parsed_doc"]
    assert "1865" in "".join(state["parsed_doc"])


# --------------------------------------------------------------------------- #
# ParseNode: warn when the answer looks one link away (issue #1120)
# --------------------------------------------------------------------------- #

POLICY_PROMPT = (
    "Does this page, or a privacy policy it links to, state that email addresses "
    "will not be sold or transferred to third parties?"
)

# The reported shape: a contact page whose notice really does exist, but on the
# policy page it links to rather than in its own text.
CONTACT_LINKING_TO_POLICY = (
    "<html><body><p>Call us on 555-0100 to book an appointment.</p>"
    '<a href="https://example.com/privacy/">Privacy Policy</a>'
    "</body></html>"
)

CONTACT_ANSWERING_ITSELF = (
    "<html><body><p>We never sell or transfer your email addresses to third "
    "parties, and our privacy policy says so.</p>"
    '<a href="https://example.com/">Home</a></body></html>'
)

CONTACT_WITHOUT_LINKS = (
    "<html><body><p>We never sell or transfer your email addresses to third "
    "parties; that is our privacy policy.</p></body></html>"
)


def test_warns_when_the_answer_is_only_behind_a_link(library_logs_propagate, caplog):
    """A term present only in a link is evidence the page was never going to answer."""
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, CONTACT_LINKING_TO_POLICY, POLICY_PROMPT)

    assert "appear only in links on this page" in caplog.text
    assert "DepthSearchGraph" in caplog.text
    assert "privacy" in caplog.text


def test_silent_when_the_page_itself_holds_the_terms(library_logs_propagate, caplog):
    """No hint when the page can answer; the warning must not fire on every link."""
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, CONTACT_ANSWERING_ITSELF, POLICY_PROMPT)

    assert "appear only in links on this page" not in caplog.text


def test_silent_when_the_page_has_no_links(library_logs_propagate, caplog):
    """With nothing linked there is no other page to point the user at."""
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, CONTACT_WITHOUT_LINKS, POLICY_PROMPT)

    assert "appear only in links on this page" not in caplog.text


def test_link_hint_does_not_stack_with_the_missing_terms_warning(
    library_logs_propagate, caplog
):
    """A page holding no trace of the request gets one warning, not two."""
    node = _parse_node()

    with caplog.at_level("WARNING"):
        _run(node, WIKIPEDIA_404, "What is the founding year of Timpson?")

    assert "None of the requested terms" in caplog.text
    assert "appear only in links on this page" not in caplog.text


def test_link_hint_leaves_the_parsed_chunks_untouched():
    """The hint only logs; parsing behaviour is unchanged."""
    node = _parse_node()
    state = _run(node, CONTACT_LINKING_TO_POLICY, POLICY_PROMPT)

    assert state["parsed_doc"]
    assert "555-0100" in "".join(state["parsed_doc"])
