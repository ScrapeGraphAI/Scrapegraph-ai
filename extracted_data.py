def extract_data(html: str) -> dict:
    from bs4 import BeautifulSoup

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Initialize an empty list to hold project data
    projects = []

    # Find all project entries in the HTML
    project_entries = soup.find_all('div', class_='grid-item')

    # Iterate over each project entry to extract title and description
    for entry in project_entries:
        # Extract the title from the card-title class
        title = entry.find('h4', class_='card-title').get_text(strip=True)
        
        # Extract the description from the card-text class
        description = entry.find('p', class_='card-text').get_text(strip=True)
        
        # Append the extracted data as a dictionary to the projects list
        projects.append({
            'title': title,
            'description': description
        })

    # Return the structured data as a dictionary matching the desired JSON schema
    return {'projects': projects}