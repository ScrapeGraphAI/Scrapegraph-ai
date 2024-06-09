import os
import pytest
from unittest.mock import patch, MagicMock
from scrapegraphai.nodes import FetchNode

def get_file_path(file_name):
    """
    Helper function to get the absolute file path.
    """
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, file_name)
    return file_path

@patch('scrapegraphai.nodes.FetchNode.execute')
def test_fetch_node_html(mock_execute):
    """
    Test FetchNode with HTML input.
    """
    mock_execute.return_value = MagicMock()
    fetch_node = FetchNode(
        input="url | local_dir",
        output=["doc"],
        node_config={
            "headless": False
        }
    )
    state = {
        "url": "https://twitter.com/home"
    }
    result = fetch_node.execute(state)
    assert result is not None
    mock_execute.assert_called_once_with(state)

@patch('scrapegraphai.nodes.FetchNode.execute')
def test_fetch_node_json(mock_execute):
    """
    Test FetchNode with JSON input.
    """
    mock_execute.return_value = MagicMock()
    file_path_json = get_file_path("inputs/example.json")
    state_json = {
        "json": file_path_json
    }
    fetch_node_json = FetchNode(
        input="json",
        output=["doc"],
    )
    result_json = fetch_node_json.execute(state_json)
    assert result_json is not None
    mock_execute.assert_called_once_with(state_json)

@patch('scrapegraphai.nodes.FetchNode.execute')
def test_fetch_node_xml(mock_execute):
    """
    Test FetchNode with XML input.
    """
    mock_execute.return_value = MagicMock()
    file_path_xml = get_file_path("inputs/books.xml")
    state_xml = {
        "xml": file_path_xml
    }
    fetch_node_xml = FetchNode(
        input="xml",
        output=["doc"],
    )
    result_xml = fetch_node_xml.execute(state_xml)
    assert result_xml is not None
    mock_execute.assert_called_once_with(state_xml)

@patch('scrapegraphai.nodes.FetchNode.execute')
def test_fetch_node_csv(mock_execute):
    """
    Test FetchNode with CSV input.
    """
    mock_execute.return_value = MagicMock()
    file_path_csv = get_file_path("inputs/username.csv")
    state_csv = {
        "csv": file_path_csv
    }
    fetch_node_csv = FetchNode(
        input="csv",
        output=["doc"],
    )
    result_csv = fetch_node_csv.execute(state_csv)
    assert result_csv is not None
    mock_execute.assert_called_once_with(state_csv)

@patch('scrapegraphai.nodes.FetchNode.execute')
def test_fetch_node_txt(mock_execute):
    """
    Test FetchNode with TXT input.
    """
    mock_execute.return_value = MagicMock()
    file_path_txt = get_file_path("inputs/plain_html_example.txt")
    state_txt = {
        "txt": file_path_txt
    }
    fetch_node_txt = FetchNode(
        input="txt",
        output=["doc"],
    )
    result_txt = fetch_node_txt.execute(state_txt)
    assert result_txt is not None
    mock_execute.assert_called_once_with(state_txt)
