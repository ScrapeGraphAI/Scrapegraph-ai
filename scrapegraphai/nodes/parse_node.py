"""
ParseNode Module
"""

import re
from typing import List, Optional, Set, Tuple, get_args
from urllib.parse import urljoin

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

    # Words carrying no discriminative signal, dropped before checking whether the
    # parsed document contains any evidence of what the user asked for.
    prompt_stopwords = frozenset(
        {
            "about",
            "after",
            "all",
            "also",
            "and",
            "any",
            "are",
            "been",
            "both",
            "but",
            "can",
            "content",
            "data",
            "does",
            "each",
            "every",
            "extract",
            "find",
            "for",
            "from",
            "get",
            "give",
            "has",
            "have",
            "here",
            "how",
            "html",
            "info",
            "information",
            "into",
            "its",
            "json",
            "list",
            "many",
            "more",
            "much",
            "must",
            "not",
            "only",
            "out",
            "page",
            "please",
            "provide",
            "retrieve",
            "return",
            "scrape",
            "site",
            "some",
            "such",
            "text",
            "that",
            "the",
            "their",
            "them",
            "then",
            "there",
            "these",
            "they",
            "this",
            "those",
            "url",
            "was",
            "web",
            "webpage",
            "website",
            "were",
            "what",
            "when",
            "where",
            "which",
            "who",
            "why",
            "will",
            "with",
            "would",
            "you",
            "your",
        }
    )

    word_pattern = re.compile(r"[a-zA-Z][a-zA-Z0-9]{2,}")
    camel_case_pattern = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")

    # Html2TextTransformer keeps links, so an anchor reaches the chunks as
    # ``[label](href)``. Used to tell a page's own prose from what it merely
    # links to.
    markdown_link_pattern = re.compile(r"\[([^\]\n]{1,200})\]\(([^)\s]{1,500})\)")

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
        self.schema = node_config.get("schema")

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

        user_prompt = state.get("user_prompt")
        if not self._warn_if_content_lacks_requested_fields(chunks, user_prompt):
            self._warn_if_answer_may_be_behind_a_link(chunks, user_prompt)

        state.update({self.output[0]: chunks})
        state.update({"parsed_doc": chunks})

        if self.parse_urls:
            state.update({self.output[1]: link_urls})
            state.update({self.output[2]: img_urls})

        return state

    def _warn_if_content_lacks_requested_fields(
        self, chunks: List[str], user_prompt: Optional[str]
    ) -> bool:
        """
        Warns when the parsed content holds no trace of what the user asked for.

        An HTTP status check catches error pages, but a perfectly valid 200 page
        can still reach the LLM without the requested data: content behind
        JavaScript that never rendered, a field living in a ``<script>`` blob the
        parser drops, or a document truncated beyond the model window. In each
        case the LLM answers ``NA`` and the run looks clean.

        This is a deterministic, LLM-free check: it collects the terms the user
        asked about (schema field names and the significant words of the prompt)
        and warns only when *none* of them appear in the parsed text. Zero
        matches is a deliberately conservative bar, so the warning stays quiet
        for legitimate runs where the answer is phrased differently from the
        question.

        Args:
            chunks (List[str]): The parsed content chunks about to be handed downstream.
            user_prompt (Optional[str]): The user's request, when available in the state.

        Returns:
            bool: True when a warning was emitted, so the caller can skip the
                narrower link check rather than warning twice about one run.
        """
        texts = [chunk for chunk in chunks if isinstance(chunk, str)]
        total_length = sum(len(text) for text in texts)

        if not any(text.strip() for text in texts):
            self.logger.warning(
                "The parsed content is empty; the model will be asked to answer "
                "from nothing. Check that the source was fetched correctly."
            )
            return True

        expected_terms = self._collect_expected_terms(user_prompt)
        if not expected_terms:
            return False

        # Chunks overlap, so a term split across a boundary is still found in one
        # of them; searching chunk by chunk avoids rebuilding the whole document.
        for text in texts:
            lowered = text.lower()
            if any(term in lowered for term in expected_terms):
                return False

        self.logger.warning(
            f"None of the requested terms {sorted(expected_terms)} appear in the "
            f"parsed content ({total_length} chars). The source may be an error "
            "page, may render its content with JavaScript, or the relevant "
            "section may have been dropped while parsing; the model will most "
            "likely answer NA."
        )
        return True

    def _warn_if_answer_may_be_behind_a_link(
        self, chunks: List[str], user_prompt: Optional[str]
    ) -> None:
        """
        Warns when the evidence for the request looks one link away.

        A single-page graph answers only about the text it was handed. When the
        answer lives on a page this one links to, a privacy policy or a terms or
        team page, the model is not silent about it: asked whether a fact holds,
        it returns a confident negative, which reads exactly like a genuine "this
        is not true of this site". That is the failure reported in #1120, and it
        is the expensive direction for compliance questions, where a false "no
        restriction found" is the answer someone acts on.

        The check is deterministic and LLM-free, like
        :meth:`_warn_if_content_lacks_requested_fields`. It warns only when a
        term the user asked about is absent from the page's own prose yet present
        in the label or target of a link. Requiring the term to be missing from
        the prose keeps the warning quiet whenever the page can actually answer,
        which is the common case.

        Args:
            chunks (List[str]): The parsed content chunks about to be handed downstream.
            user_prompt (Optional[str]): The user's request, when available in the state.
        """
        texts = [chunk for chunk in chunks if isinstance(chunk, str)]
        if not texts:
            return

        missing = self._collect_expected_terms(user_prompt)
        if not missing:
            return

        links: List[Tuple[str, str]] = []
        # Chunks overlap, so a term is "missing" only when no chunk's prose holds
        # it. Narrowing chunk by chunk avoids rebuilding the whole document.
        for text in texts:
            links.extend(self.markdown_link_pattern.findall(text))
            prose = self.markdown_link_pattern.sub(" ", text).lower()
            missing = {term for term in missing if term not in prose}
            if not missing:
                return

        if not links:
            return

        linked_terms: Set[str] = set()
        examples: List[str] = []
        for label, href in links:
            target = f"{label} {href}".lower()
            hits = {term for term in missing if term in target}
            if not hits:
                continue
            linked_terms |= hits
            if href not in examples and len(examples) < 3:
                examples.append(href)

        if not linked_terms:
            return

        self.logger.warning(
            f"The terms {sorted(linked_terms)} appear only in links on this page "
            f"(e.g. {examples}), not in its text. This graph reads the single page "
            "it was given, so if the answer lives on one of those linked pages the "
            "model will answer from the page it did see, and a negative answer here "
            "may mean the evidence was never fetched rather than that it does not "
            "exist. Consider DepthSearchGraph to follow the links."
        )

    def _collect_expected_terms(self, user_prompt: Optional[str]) -> Set[str]:
        """
        Builds the set of lowercase terms that evidence the user's request.

        Args:
            user_prompt (Optional[str]): The user's request, when available.

        Returns:
            Set[str]: Significant terms drawn from the schema field names and the
                prompt; empty when nothing discriminative could be derived.
        """
        terms = self._schema_field_terms(self.schema)

        if isinstance(user_prompt, str):
            terms |= self._significant_words(user_prompt)

        return terms

    @classmethod
    def _significant_words(cls, text: str) -> Set[str]:
        """
        Extracts the discriminative words of a piece of text.

        Args:
            text (str): The text to tokenize.

        Returns:
            Set[str]: Lowercase words at least three characters long that are not
                generic scraping vocabulary.
        """
        words = cls.word_pattern.findall(cls.camel_case_pattern.sub(" ", text))
        return {
            word.lower() for word in words if word.lower() not in cls.prompt_stopwords
        }

    @classmethod
    def _schema_field_terms(cls, schema, _depth: int = 0) -> Set[str]:
        """
        Extracts the field names of an output schema, recursing into nested ones.

        Supports the schema flavours the library accepts: Pydantic models, plain
        JSON Schema dictionaries, and lists of either.

        Args:
            schema: The output schema, in any of the supported forms; may be None.
            _depth (int): Internal recursion guard for deeply nested schemas.

        Returns:
            Set[str]: Lowercase terms derived from the field names, with
                ``snake_case`` and ``camelCase`` names split into their parts.
        """
        if schema is None or _depth > 5:
            return set()

        names: List[str] = []
        terms: Set[str] = set()

        if isinstance(schema, dict):
            properties = schema.get("properties")
            if isinstance(properties, dict):
                names.extend(str(key) for key in properties)
                for value in properties.values():
                    terms |= cls._schema_field_terms(value, _depth + 1)
            items = schema.get("items")
            if items is not None:
                terms |= cls._schema_field_terms(items, _depth + 1)
        elif isinstance(schema, (list, tuple, set)):
            for entry in schema:
                terms |= cls._schema_field_terms(entry, _depth + 1)
        else:
            model_fields = getattr(schema, "model_fields", None)  # pydantic v2
            if model_fields is None:
                model_fields = getattr(schema, "__fields__", None)  # pydantic v1
            if isinstance(model_fields, dict):
                names.extend(str(key) for key in model_fields)
                for field in model_fields.values():
                    annotation = getattr(field, "annotation", None)
                    for nested in cls._nested_models(annotation):
                        terms |= cls._schema_field_terms(nested, _depth + 1)

        for name in names:
            terms |= cls._significant_words(name.replace("_", " "))

        return terms

    @staticmethod
    def _nested_models(annotation) -> List:
        """
        Finds the Pydantic models reachable from a field annotation.

        Unwraps the typing containers schemas commonly use — ``List[Item]``,
        ``Optional[Item]``, ``Dict[str, Item]`` — so nested field names are not
        lost.

        Args:
            annotation: The annotation of a Pydantic field; may be None.

        Returns:
            List: The Pydantic model classes found in the annotation.
        """
        if annotation is None:
            return []

        if hasattr(annotation, "model_fields") or hasattr(annotation, "__fields__"):
            return [annotation]

        return [
            arg
            for arg in get_args(annotation)
            if hasattr(arg, "model_fields") or hasattr(arg, "__fields__")
        ]

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
        if not source.startswith("http"):
            all_urls = [url for url in all_urls if url.startswith("http")]
        else:
            all_urls = [urljoin(source, url) for url in all_urls]

        images = [
            url
            for url in all_urls
            if any(url.endswith(ext) for ext in image_extensions)
        ]
        links = [url for url in all_urls if url not in images]

        return links, images

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
