"""
This utility function transforms the pydantic schema into a more comprehensible schema.
"""


def transform_schema(pydantic_schema):
    """
    Transform the pydantic schema into a more comprehensible JSON schema.

    Args:
        pydantic_schema (dict): The pydantic schema.

    Returns:
        dict: The transformed JSON schema.
    """

    def process_properties(properties):
        result = {}
        for key, value in properties.items():
            if "type" in value:
                if value["type"] == "array":
                    if "items" in value and "$ref" in value["items"]:
                        ref_key = value["items"]["$ref"].split("/")[-1]
                        if "$defs" in pydantic_schema and ref_key in pydantic_schema["$defs"]:
                            result[key] = [
                                process_properties(
                                    pydantic_schema["$defs"][ref_key].get("properties", {})
                                )
                            ]
                        else:
                            result[key] = ["object"]  # fallback for missing reference
                    elif "items" in value and "type" in value["items"]:
                        result[key] = [value["items"]["type"]]
                    else:
                        result[key] = ["unknown"]  # fallback for malformed array
                else:
                    result[key] = {
                        "type": value["type"],
                        "description": value.get("description", ""),
                    }
            elif "$ref" in value:
                ref_key = value["$ref"].split("/")[-1]
                if "$defs" in pydantic_schema and ref_key in pydantic_schema["$defs"]:
                    result[key] = process_properties(
                        pydantic_schema["$defs"][ref_key].get("properties", {})
                    )
                else:
                    result[key] = {"type": "object", "description": "Missing reference"}  # fallback
        return result

    if "properties" not in pydantic_schema:
        raise ValueError("Invalid pydantic schema: missing 'properties' key")
    return process_properties(pydantic_schema["properties"])
