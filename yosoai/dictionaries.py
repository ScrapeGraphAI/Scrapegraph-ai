schema_example= { 
    "properties": { 
        "person_name": {"type": "string"}, 
        "person_surname": {"type": "string"}, 
        "profession": {"type": "string"}, 
        "hobbies": {"type": "string"}, 
        "projects": { 
            "type": "array", 
            "items": { 
                "type": "object", 
                "properties": { 
                    "project_name": {"type": "string"}, 
                    "project_description": {"type": "string"}, 
                    "url": {"type": "string"} 
                },
                "required": ["project_name", "project_description", "url"], 
            }, 
        }, 
    }, 
    "required": ["person_name", "person_surname", "profession", "hobbies", "projects"], 
}

models_tokens = {
    "gpt-3.5-turbo-0125": 16385,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-1106": 16385,
    "gpt-3.5-turbo-instruct": 4096,
    "gpt-4-0125-preview": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4-1106-preview": 128000,
    "gpt-4-vision-preview": 128000,
    "gpt-4": 8192,
    "gpt-4-0613": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
}