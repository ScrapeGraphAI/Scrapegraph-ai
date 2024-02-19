graph_schema = {
  "name": "ScrapeGraphAI Graph Configuration",
  "description": "JSON schema for representing graphs in the ScrapeGraphAI library",
  "type": "object",
  "properties": {
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "node_name": {
            "type": "string",
            "description": "The unique identifier for the node."
          },
          "node_type": {
            "type": "string",
            "description": "The type of node, must be 'node' or 'conditional_node'."
          },
          "args": {
            "type": "object",
            "description": "The arguments required for the node's execution."
          },
          "returns": {
            "type": "object",
            "description": "The return values of the node's execution."
           },
        },
        "required": ["node_name", "node_type", "args", "returns"]
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "from": {
            "type": "string",
            "description": "The node_name of the starting node of the edge."
          },
          "to": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "An array containing the node_names of the ending nodes of the edge. If the 'from' node is a conditional node, this array must contain exactly two node_names."
          }
        },
        "required": ["from", "to"]
      }
    },
    "entry_point": {
      "type": "string",
      "description": "The node_name of the entry point node."
    }
  },
  "required": ["nodes", "edges", "entry_point"]
}