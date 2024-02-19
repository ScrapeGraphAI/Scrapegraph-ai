"""
Nodes metadata for the scrapegraphai package.
"""

nodes_metadata = {
    "FetchHTMLNode": {
        "description": "Fetches HTML content from a given URL.",
        "type": "node",
        "args": {
            "url": "The URL from which to fetch HTML content."
        },
        "returns": "Updated state with fetched HTML content under 'document' key."
    },
    "GetProbableTagsNode": {
        "description": "Identifies probable HTML tags from a document based on a user's question.",
        "type": "node",
        "args": {
            "user_input": "User's query or question.",
            "document": "HTML content as a string."
        },
        "returns": "Updated state with probable HTML tags under 'tags' key."
    },
    "ParseHTMLNode": {
        "description": "Parses HTML content to extract specific data.",
        "type": "node",
        "args": {
            "document": "HTML content as a string.",
            "tags": "List of HTML tags to focus on during parsing."
        },
        "returns": "Updated state with extracted data under 'parsed_document' key."
    },
    "GenerateAnswerNode": {
        "description": "Generates an answer based on the user's input and parsed document.",
        "type": "node",
        "args": {
            "user_input": "User's query or question.",
            "parsed_document": "Data extracted from the HTML document."
        },
        "returns": "Updated state with the answer under 'answer' key."
    },
    "ConditionalNode": {
        "description": "Decides the next node to execute based on a condition.",
        "type": "conditional_node",
        "args": {
            "key_name": "The key in the state to check for a condition.",
            "next_nodes": "A list of two nodes specifying the next node to execute based on the condition's outcome."
        },
        "returns": "The name of the next node to execute."
    },
    "ImageToTextNode": {
        "description": "Converts image content to text by extracting visual information and interpreting it.",
        "type": "node",
        "args": {
            "image_data": "Data of the image to be processed."
        },
        "returns": "Updated state with the textual description of the image under 'image_text' key."
    },
    "TextToSpeechNode": {
        "description": "Converts text into spoken words, allowing for auditory representation of the text.",
        "type": "node",
        "args": {
            "text": "The text to be converted into speech."
        },
        "returns": "Updated state with the speech audio file or data under 'speech_audio' key."
    }
}