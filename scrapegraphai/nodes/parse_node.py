"""
ParseNode Module
"""

import re
from typing import List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document

from ..helpers import default_filters
from ..utils.split_text_into_chunks import split_text_into_chunks
from .base_node import BaseNode


class ParseNode(BaseNode):
    """
    A node responsible for parsing HTML content from a document.
    The parsed content is split into chunks for further processing.

    This node enhances the scraping workflow by allowing for targeted extraction of
    content, thereby optimizing the processing of large HTML documents.

    Attributes:
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Parse".
    """

    url_pattern = re.compile(
        r"[http[s]?:\/\/]?(www\.)?([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)"
    )
    relative_url_pattern = re.compile(r"[\(](/[^\(\)\s]*)")

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "ParseNode",
    ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.parse_html = (
            True if node_config is None else node_config.get("parse_html", True)
        )
        self.parse_urls = (
            False if node_config is None else node_config.get("parse_urls", False)
        )

        self.llm_model = node_config.get("llm_model")
        self.chunk_size = node_config.get("chunk_size")

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to parse the HTML document content and split it into chunks.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data from the state.

        Returns:
            dict: The updated state with the output key containing the parsed content chunks.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for parsing the content is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        input_keys = self.get_input_keys(state)
        input_data = [state[key] for key in input_keys]
        docs_transformed = input_data[0]
        source = input_data[1] if self.parse_urls else None

        raw_html = None
        if isinstance(docs_transformed, list) and docs_transformed:
            first_doc = docs_transformed[0]
            if isinstance(first_doc, Document):
                raw_html = first_doc.page_content

        if self.parse_html:
            docs_transformed = Html2TextTransformer(
                ignore_links=False
            ).transform_documents(input_data[0])
            docs_transformed = docs_transformed[0]

            link_urls, img_urls = self._extract_urls(
                docs_transformed.page_content, source
            )

            chunks = split_text_into_chunks(
                text=docs_transformed.page_content,
                chunk_size=self.chunk_size - 250,
            )
        else:
            docs_transformed = docs_transformed[0]

            try:
                link_urls, img_urls = self._extract_urls(
                    docs_transformed.page_content, source
                )
            except Exception:
                link_urls, img_urls = "", ""

            chunk_size = self.chunk_size
            chunk_size = min(chunk_size - 500, int(chunk_size * 0.8))

            if isinstance(docs_transformed, Document):
                chunks = split_text_into_chunks(
                    text=docs_transformed.page_content,
                    chunk_size=chunk_size,
                )
            else:
                chunks = split_text_into_chunks(
                    text=docs_transformed, chunk_size=chunk_size
                )

        state.update({self.output[0]: chunks})
        state.update({"parsed_doc": chunks})

        img_metadata = []
        if self.parse_urls:
            if raw_html:
                img_metadata = self._extract_img_metadata(raw_html, source)

            if img_metadata:
                img_urls = [meta["url"] for meta in img_metadata]

            state.update({self.output[1]: link_urls})
            state.update({self.output[2]: img_urls})
            state["img_metadata"] = img_metadata

        return state

    def _extract_urls(self, text: str, source: str) -> Tuple[List[str], List[str]]:
        """
        Extracts URLs from the given text.

        Args:
            text (str): The text to extract URLs from.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing the extracted link URLs and image URLs.
        """
        if not self.parse_urls:
            return [], []

        image_extensions = default_filters.filter_dict["img_exts"]
        url = ""
        all_urls = set()

        for group in ParseNode.url_pattern.findall(text):
            for el in group:
                if el != "":
                    url += el
            all_urls.add(url)
            url = ""

        url = ""
        for group in ParseNode.relative_url_pattern.findall(text):
            for el in group:
                if el not in ["", "[", "]", "(", ")", "{", "}"]:
                    url += el
            all_urls.add(urljoin(source, url))
            url = ""

        all_urls = list(all_urls)
        all_urls = self._clean_urls(all_urls)
        normalized_urls = []
        for url in all_urls:
            normalized = self._normalize_url(url, source)
            if normalized:
                normalized_urls.append(normalized)

        all_urls = normalized_urls

        images = [
            url
            for url in all_urls
            if any(url.lower().endswith(ext) for ext in image_extensions)
        ]
        links = [url for url in all_urls if url not in images]

        return links, images

    def _extract_img_metadata(self, html: str, source: Optional[str]) -> List[dict]:
        """Extract image URLs and alt text directly from the HTML."""
        if not html:
            return []

        metadata = []
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception:
            return metadata

        seen = set()

        def add_entry(url: Optional[str], alt: str = ""):
            normalized = self._normalize_url(url, source)
            if not normalized or normalized in seen:
                return
            seen.add(normalized)
            metadata.append({"url": normalized, "alt": alt.strip()})

        for picture in soup.find_all("picture"):
            img_tag = picture.find("img")
            base_alt = (img_tag.get("alt") if img_tag else "") or picture.get("title", "")

            for source_tag in picture.find_all("source"):
                srcset = source_tag.get("srcset", "")
                src = self._select_from_srcset(srcset)
                if not src:
                    continue
                alt_candidate = source_tag.get("title") or base_alt
                add_entry(src, alt_candidate)

            if img_tag:
                add_entry(img_tag.get("src"), base_alt)

        for img in soup.find_all("img"):
            src = (img.get("src") or "").strip()
            if not src or src.startswith("data:"):
                continue
            add_entry(src, img.get("alt", ""))

        for source_tag in soup.find_all("source"):
            srcset = source_tag.get("srcset", "")
            src = self._select_from_srcset(srcset)
            if not src:
                continue
            alt_candidate = source_tag.get("title") or ""
            add_entry(src, alt_candidate)

        # Elements with inline background images
        for elem in soup.find_all(style=re.compile(r"background", re.IGNORECASE)):
            style_attr = elem.get("style", "")
            for bg_url in self._extract_background_urls(style_attr):
                alt_candidate = (
                    elem.get("aria-label")
                    or elem.get("data-title")
                    or elem.get_text(strip=True)
                )
                add_entry(bg_url, alt_candidate)

        # data-background-image or data-src attributes (common in sliders)
        for elem in soup.find_all(attrs={"data-background-image": True}):
            bg_url = elem.get("data-background-image")
            alt_candidate = (
                elem.get("aria-label")
                or elem.get("data-title")
                or elem.get_text(strip=True)
            )
            add_entry(bg_url, alt_candidate)

        for elem in soup.find_all(attrs={"data-src": True}):
            bg_url = elem.get("data-src")
            alt_candidate = elem.get("alt") or elem.get_text(strip=True)
            add_entry(bg_url, alt_candidate)

        return metadata

    @staticmethod
    def _select_from_srcset(srcset: str) -> Optional[str]:
        if not srcset:
            return None
        best_url = None
        best_width = -1
        for candidate in srcset.split(","):
            parts = candidate.strip().split()
            if not parts:
                continue
            url = parts[0]
            width = -1
            if len(parts) > 1 and parts[1].endswith("w"):
                try:
                    width = int(parts[1][:-1])
                except ValueError:
                    width = -1
            if best_url is None or width > best_width:
                best_url = url
                best_width = width
        return best_url

    @staticmethod
    def _extract_background_urls(style: str) -> List[str]:
        if not style:
            return []
        urls = []
        matches = re.findall(r"background(?:-image)?\s*:\s*url\(([^)]+)\)", style, flags=re.IGNORECASE)
        for raw in matches:
            cleaned = raw.strip().strip('"\'')
            if cleaned:
                urls.append(cleaned)
        return urls

    def _normalize_url(self, url: str, source: Optional[str]) -> Optional[str]:
        """Normalize relative or protocol-relative URLs to absolute ones."""
        if not url:
            return None

        url = url.strip()

        if url.startswith("data:"):
            return None

        if url.startswith("http://") or url.startswith("https://"):
            return url

        if url.startswith("//"):
            return f"https:{url}"

        if re.match(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?$", url):
            return f"https://{url}"

        if source and source.startswith("http"):
            return urljoin(source, url)

        return None

    def _clean_urls(self, urls: List[str]) -> List[str]:
        """
        Cleans the URLs extracted from the text.

        Args:
            urls (List[str]): The list of URLs to clean.

        Returns:
            List[str]: The cleaned URLs.
        """
        cleaned_urls = []
        for url in urls:
            if not ParseNode._is_valid_url(url):
                url = re.sub(r".*?\]\(", "", url)
                url = re.sub(r".*?\[\(", "", url)
                url = re.sub(r".*?\[\)", "", url)
                url = re.sub(r".*?\]\)", "", url)
                url = re.sub(r".*?\)\[", "", url)
                url = re.sub(r".*?\)\[", "", url)
                url = re.sub(r".*?\(\]", "", url)
                url = re.sub(r".*?\)\]", "", url)
            url = url.rstrip(").-")
            if len(url) > 0:
                cleaned_urls.append(url)

        return cleaned_urls

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        CHecks if the URL format is valid.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL format is valid, False otherwise
        """
        if re.fullmatch(ParseNode.url_pattern, url) is not None:
            return True
        return False
