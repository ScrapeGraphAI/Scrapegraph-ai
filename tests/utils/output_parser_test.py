"""Tests for scrapegraphai.utils.output_parser.TolerantJsonOutputParser."""

import pytest

from scrapegraphai.utils.output_parser import (
    TolerantJsonOutputParser,
    _strip_doubled_braces,
)


def test_strip_doubled_braces_unwraps_single_layer():
    assert _strip_doubled_braces('{{"content": "hi"}}') == '{"content": "hi"}'


def test_strip_doubled_braces_is_noop_for_clean_json():
    text = '{"content": "hi"}'
    assert _strip_doubled_braces(text) == text


def test_strip_doubled_braces_ignores_unbalanced():
    text = '{{"content": "hi"}'
    assert _strip_doubled_braces(text) == text


def test_tolerant_parser_parses_clean_json_unchanged():
    parser = TolerantJsonOutputParser()
    assert parser.parse('{"content": "hi"}') == {"content": "hi"}


def test_tolerant_parser_recovers_doubled_braces():
    """Models such as DeepSeek echo the prompt's escaped braces verbatim."""
    parser = TolerantJsonOutputParser()
    assert parser.parse('{{"content": "hi"}}') == {"content": "hi"}


def test_tolerant_parser_recovers_doubled_braces_with_whitespace():
    parser = TolerantJsonOutputParser()
    assert parser.parse('  {{"content": "hi"}}  ') == {"content": "hi"}


def test_tolerant_parser_still_raises_on_irrecoverable_output():
    parser = TolerantJsonOutputParser()
    with pytest.raises(Exception):
        parser.parse("this is not json at all")
