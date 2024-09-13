from bs4 import BeautifulSoup
import re

def extract_book_info(html_string):
    """
    Extracts book information (title, author, publication date, publisher) from an HTML string using BeautifulSoup.

    Args:
        html_string: The HTML content as a string.

    Returns:
        A dictionary containing the extracted book information in the desired JSON schema format.
    """

    soup = BeautifulSoup(html_string, 'html.parser')

    # Find all book listings
    book_listings = soup.find_all('div', class_='cc-product-list-item')

    books_data = []
    for listing in book_listings:
        # Extract title
        title_elem = listing.find('a', class_='cc-title')
        title = title_elem.text.strip() if title_elem else None

        # Extract author
        author_elem = listing.find('div', class_='cc-author').find('a', class_='cc-author-name')
        author = author_elem.text.strip() if author_elem else None

        # Extract publisher and publication date
        publisher_info_elem = listing.find('span', class_='cc-publisher')
        publisher_info_text = publisher_info_elem.text.strip() if publisher_info_elem else None

        if publisher_info_text:
            # Assuming publisher name is linked and publication date is the remaining text
            publisher_elem = publisher_info_elem.find('a', class_='cc-publisher-name')
            publisher = publisher_elem.text.strip() if publisher_elem else None

            # Use regex to extract year (assuming 4-digit year format)
            publication_date_match = re.search(r'\b(\d{4})\b', publisher_info_text)
            publication_date = publication_date_match.group(1) if publication_date_match else None
        else:
            publisher = None
            publication_date = None

        # Create a book dictionary and append to the list
        book_data = {
            "title": title,
            "author": author,
            "publication_date": publication_date,
            "publisher": publisher
        }
        books_data.append(book_data)

    # Structure the output according to the JSON schema
    output = {
        "books": books_data
    }

    return output

html = open('example_1.html').read()
result = extract_book_info(html)
print(result)