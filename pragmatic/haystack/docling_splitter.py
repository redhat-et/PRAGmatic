from typing import Any, Dict, List

from docling_core.types import DoclingDocument

from haystack import Document, component
from haystack.core.serialization import default_from_dict, default_to_dict

from docling.chunking import HybridChunker


@component
class DoclingDocumentSplitter:

    SUPPORTED_CONTENT_FORMATS = ['json']

    def __init__(self, embedding_model_id=None, content_format=None, max_tokens=None):
        self.__chunker = HybridChunker(tokenizer=embedding_model_id, max_tokens=max_tokens)
        self.__embedding_model_id = embedding_model_id

        if content_format not in self.SUPPORTED_CONTENT_FORMATS:
            raise ValueError(f"Only the following input formats are currently supported: {self.SUPPORTED_CONTENT_FORMATS}.")
        self.__content_format = content_format

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        if not isinstance(documents, list) or (documents and not isinstance(documents[0], Document)):
            raise TypeError("DoclingDocumentSplitter expects a List of Documents as input.")

        split_docs = []
        for doc in documents:
            if doc.content is None:
                raise ValueError(f"Missing content for document ID {doc.id}.")

            chunks = self._split_with_docling(doc.content)
            current_split_docs = [Document(content=chunk) for chunk in chunks]
            split_docs.extend(current_split_docs)

        return {"documents": split_docs}

    def _split_with_docling(self, text: str) -> List[str]:
        if self.__content_format == 'json':
            document = DoclingDocument.model_validate_json(text)
        else:
            raise ValueError(f"Unexpected content format {self.__content_format}")

        chunk_iter = self.__chunker.chunk(dl_doc=document)
        chunks = list(chunk_iter)
        return [self.__chunker.serialize(chunk=chunk) for chunk in chunks]

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.
        """
        return default_to_dict(self, embedding_model_id=self.__embedding_model_id, content_format=self.__content_format)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DoclingDocumentSplitter":
        """
        Deserializes the component from a dictionary.
        """
        return default_from_dict(cls, data)