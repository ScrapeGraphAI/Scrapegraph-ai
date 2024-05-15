import os
import pytest
from scrapegraphai.nodes import FetchNode

def test_fetch_node_html():
    """
    Run the tests
    """
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

def test_fetch_node_json():
    """
    Run the tests
    """
    FILE_NAME_JSON = "inputs/example.json"
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path_json = os.path.join(curr_dir, FILE_NAME_JSON)

    state_json = {
        "json": file_path_json
    }

    fetch_node_json = FetchNode(
        input="json",
        output=["doc"],
    )

    result_json = fetch_node_json.execute(state_json)

    assert result_json is not None

def test_fetch_node_xml():
    """
    Run the tests
    """
    FILE_NAME_XML = "inputs/books.xml"
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path_xml = os.path.join(curr_dir, FILE_NAME_XML)

    state_xml = {
        "xml": file_path_xml
    }

    fetch_node_xml = FetchNode(
        input="xml",
        output=["doc"],
    )

    result_xml = fetch_node_xml.execute(state_xml)

    assert result_xml is not None

def test_fetch_node_csv():
    """
    Run the tests
    """
    FILE_NAME_CSV = "inputs/username.csv"
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path_csv = os.path.join(curr_dir, FILE_NAME_CSV)

    state_csv = {
        "csv": file_path_csv  # Definire un dizionario con la chiave "csv" e il valore come percorso del file CSV
    }

    fetch_node_csv = FetchNode(
        input="csv",
        output=["doc"],
    )

    result_csv = fetch_node_csv.execute(state_csv)

    assert result_csv is not None

def test_fetch_node_txt():
    """
    Run the tests
    """
    FILE_NAME_TXT = "inputs/plain_html_example.txt"
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path_txt = os.path.join(curr_dir, FILE_NAME_TXT)

    state_txt = {
        "txt": file_path_txt  # Definire un dizionario con la chiave "txt" e il valore come percorso del file TXT
    }

    fetch_node_txt = FetchNode(
        input="txt",
        output=["doc"],
    )

    result_txt = fetch_node_txt.execute(state_txt)

    assert result_txt is not None
