""" 
Example of the remover method
"""
from scrapegraphai.utils.remover import remover

HTML_CONTENT = """
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>This is a Test</h1>
    <p>Hello, World!</p>
    <script>alert("This is a script");</script>
</body>
</html>
"""

parsed_content = remover(HTML_CONTENT)

print(parsed_content)
