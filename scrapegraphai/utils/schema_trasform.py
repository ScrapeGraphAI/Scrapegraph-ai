"""
This utility function trasfrom the pydantic schema into a more comprehensible schema.
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
            if 'type' in value:
                if value['type'] == 'array':
                    if '$ref' in value['items']:
                        ref_key = value['items']['$ref'].split('/')[-1]
                        result[key] = [process_properties(
                                                            pydantic_schema['$defs'][ref_key]['properties'])]
                    else:
                        result[key] = [value['items']['type']]
                else:
                    result[key] = {
                        "type": value['type'],
                        "description": value.get('description', '')
                    }
            elif '$ref' in value:
                ref_key = value['$ref'].split('/')[-1]
                result[key] = process_properties(pydantic_schema['$defs'][ref_key]['properties'])
        return result

    return process_properties(pydantic_schema['properties'])
