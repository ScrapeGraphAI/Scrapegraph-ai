---
title: ScrapGraphAI Roadmap
markmap:
  colorFreezeLevel: 2
  maxWidth: 500
---

# **ScrapGraphAI Roadmap**

## **Short-Term Goals**

- Improve the documentation (ReadTheDocs)
    - [Issue #102](https://github.com/VinciGit00/Scrapegraph-ai/issues/102)

- Create tutorials for the library

## **Medium-Term Goals**

- Node for handling API requests
- Make scraping more deterministic
    - Create DOM tree of the website
    - HTML tag text embeddings with tags metadata
    - Study tree forks from root node
    - How do we use the tags parameters?

- Create scraping folder with report
    - Folder contains .scrape files, DOM tree files, report
    - Report could be a HTML page with scraping speed, costs, LLM info, scraped content and DOM tree visualization
    - We can use pyecharts with R-markdown

- Scrape multiple pages of the same website
    - Create new node that instantiate multiple graphs at the same time
    - Make graphs run in parallel
    - Scrape only relevant URLs from user prompt
    - Use the multi dimensional DOM tree of the website for retrieval

- Crawler graph
    - Scrape all the URLs with the same domain in all the pages
    - Build many DOM trees and link them together
    - Save the multi dimensional tree in a file

- Compare two DOM trees to assess the similarity
    - Save the DOM tree of the scraped website in a file as a sort of cache to be used to compare with future website structure
    - Create similarity metrics with multiple DOM trees (overall tree? only relevant tags structure?)

- Nodes for handling authentication
    - Use Selenium or Playwright to handle authentication
    - Passes the cookies to the other nodes

- Nodes that attaches to an open browser
    - Use Selenium or Playwright to attach to an open browser
    - Navigate inside the browser and scrape the content

- Nodes for taking screenshots and understanding the page layout
    - Use Selenium or Playwright to take screenshots
    - Use LLM to asses if it is a block-like page, paragraph-like page, etc.
    - [Issue #88](https://github.com/VinciGit00/Scrapegraph-ai/issues/88)
    
## **Long-Term Goals**

- Automatic generation of scraping pipelines from a given prompt

- Create API for the library
