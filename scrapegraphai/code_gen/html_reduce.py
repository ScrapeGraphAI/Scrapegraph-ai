import re
from bs4 import BeautifulSoup, Comment


def minify_html(html):
    # Remove comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove whitespace between tags
    html = re.sub(r'>\s+<', '><', html)
    
    # Remove whitespace at the beginning and end of tags
    html = re.sub(r'\s+>', '>', html)
    html = re.sub(r'<\s+', '<', html)
    
    # Collapse multiple whitespace characters into a single space
    html = re.sub(r'\s+', ' ', html)
    
    # Remove spaces around equals signs in attributes
    html = re.sub(r'\s*=\s*', '=', html)
    
    return html.strip()

def reduce_html(html, reduction):
    """
    html: str, the HTML content to reduce
    reduction: 0: minification only,
               1: minification and removig unnecessary tags and attributes,
               2: minification, removig unnecessary tags and attributes, simplifying text content, removing of the head tag
    
    
    """
    if reduction == 0:
        return minify_html(html)
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Remove script and style tag contents, but keep the tags
    for tag in soup(['script', 'style']):
        tag.string = ""
    
    # Remove unnecessary attributes, but keep class and id
    attrs_to_keep = ['class', 'id', 'href', 'src']
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr not in attrs_to_keep:
                del tag[attr]
                
    if reduction == 1:
        return minify_html(str(soup))
    
    # Remove script and style tags completely
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    # Focus only on the body
    body = soup.body
    if not body:
        return "No <body> tag found in the HTML"
    
    # Simplify text content
    for tag in body.find_all(string=True):
        if tag.parent.name not in ['script', 'style']:
            tag.replace_with(re.sub(r'\s+', ' ', tag.strip())[:20])
    
    # Generate reduced HTML
    reduced_html = str(body)
    
    # Apply minification
    reduced_html = minify_html(reduced_html)
    
    return reduced_html

# Get string with html from example.html
html = open('example_1.html').read()

reduced_html = reduce_html(html, 2)

# Print the reduced html in result.html
with open('result_1.html', 'w') as f:
    f.write(reduced_html)