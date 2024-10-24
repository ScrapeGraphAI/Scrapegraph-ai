"""
data_export module 
This module provides functions to export data to various file formats.
"""
import json
import csv
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def export_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Export data to a JSON file.
    
    :param data: List of dictionaries containing the data to export
    :param filename: Name of the file to save the JSON data
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data exported to {filename}")

def export_to_csv(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Export data to a CSV file.
    
    :param data: List of dictionaries containing the data to export
    :param filename: Name of the file to save the CSV data
    """
    if not data:
        print("No data to export")
        return

    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data exported to {filename}")

def export_to_xml(data: List[Dict[str, Any]], filename: str, root_element: str = "data") -> None:
    """
    Export data to an XML file.
    
    :param data: List of dictionaries containing the data to export
    :param filename: Name of the file to save the XML data
    :param root_element: Name of the root element in the XML structure
    """
    root = ET.Element(root_element)
    for item in data:
        element = ET.SubElement(root, "item")
        for key, value in item.items():
            sub_element = ET.SubElement(element, key)
            sub_element.text = str(value)

    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f"Data exported to {filename}")

