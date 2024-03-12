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
    "ParseNode": {
        "description": "Parses document content to extract specific data.",
        "type": "node",
        "args": {
            "doc_type": "Type of the input document. Default is 'html'.",
            "document": "The document content to be parsed.",
        },
        "returns": "Updated state with extracted data under 'parsed_document' key."
    },
    "RAGNode": {
        "description": """A node responsible for reducing the amount of text to be processed 
        by identifying and retrieving the most relevant chunks of text based on the user's query. 
        Utilizes RecursiveCharacterTextSplitter for chunking, Html2TextTransformer for HTML to text 
        conversion, and a combination of FAISS and OpenAIEmbeddings 
        for efficient information retrieval.""",
        "type": "node",
        "args": {
            "user_input": "The user's query or question guiding the retrieval.",
            "document": "The document content to be processed and compressed."
        },
        "returns": """Updated state with 'relevant_chunks' key containing
         the most relevant text chunks."""
    },
    "GenerateAnswerNode": {
        "description": "Generates an answer based on the user's input and parsed document.",
        "type": "node",
        "args": {
            "user_input": "User's query or question.",
            "parsed_document": "Data extracted from the input document."
        },
        "returns": "Updated state with the answer under 'answer' key."
    },
    "ConditionalNode": {
        "description": "Decides the next node to execute based on a condition.",
        "type": "conditional_node",
        "args": {
            "key_name": "The key in the state to check for a condition.",
            "next_nodes": """A list of two nodes specifying the next node 
            to execute based on the condition's outcome."""
        },
        "returns": "The name of the next node to execute."
    },
    "ImageToTextNode": {
        "description": """Converts image content to text by 
        extracting visual information and interpreting it.""",
        "type": "node",
        "args": {
            "image_data": "Data of the image to be processed."
        },
        "returns": "Updated state with the textual description of the image under 'image_text' key."
    },
    "TextToSpeechNode": {
        "description": """Converts text into spoken words, allow
        ing for auditory representation of the text.""",
        "type": "node",
        "args": {
            "text": "The text to be converted into speech."
        },
        "returns": "Updated state with the speech audio file or data under 'speech_audio' key."
    }
}
