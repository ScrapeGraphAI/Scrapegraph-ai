from typing import Any, AsyncIterator, Iterator, List, Optional
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from langchain_community.document_loaders import FireCrawlLoader

class FirecrawlLoader(BaseLoader):
    """Fetches HTML pages from URLs using FireCrawlLoader API

    Attributes:
        urls: A list of URLs to fetch content from.
        mode: The mode for FireCrawlLoader, defaults to "scrape".
        params: Additional parameters for FireCrawlLoader.
    """

    def __init__(
        self,
        urls: List[str],
        *,
        mode: str = "scrape",
        params: Optional[dict] = None,
        **kwargs: Any,
    ):
        """Initialize the loader with a list of URL paths.

        Args:
            urls: A list of URLs to fetch content from.
            mode: The mode for FireCrawlLoader, defaults to "scrape".
            params: Additional parameters for FireCrawlLoader.
            kwargs: Additional keyword arguments (unused, for compatibility).
        """
        self.urls = urls
        self.mode = mode
        # Only fetch main content, no headers, footers, etc.
        self.params = params or {"onlyMainContent": True} 
        print('Using FireCrawlLoader')

    def lazy_load(self) -> Iterator[Document]:
        """
        Lazily load content from the provided URLs using FireCrawlLoader.

        This method yields Documents one at a time as they're fetched,
        instead of waiting to fetch all URLs before returning.

        Yields:
            Document: The fetched content encapsulated within a Document object.
        """
        for url in self.urls:
            loader = FireCrawlLoader(url=url, mode=self.mode, params=self.params)
            docs = loader.load()
            
            if docs:
                # Assuming FireCrawlLoader returns a list with at least one Document
                doc = docs[0]
                # Reformat the document to fit scrapegraphai's Document format
                content = f"Title: {doc.metadata.get('title', '')}\nDescription: {doc.metadata.get('description', '')}"
                metadata = {'source': url}
                yield Document(page_content=content, metadata=metadata)

    async def alazy_load(self) -> AsyncIterator[Document]:
        """
        Asynchronously load content from the provided URLs.

        This method mimics the async behavior of the original ChromiumLoader,
        but since FireCrawlLoader doesn't have an async API, it falls back to
        using the synchronous lazy_load method.

        Yields:
            Document: A Document object containing the fetched content, along with its
            source URL as metadata.
        """
        for document in self.lazy_load():
            yield document

    def load(self) -> List[Document]:
        """
        Load all documents from the provided URLs.

        Returns:
            List[Document]: A list of Document objects containing the fetched content.
        """
        return list(self.lazy_load())