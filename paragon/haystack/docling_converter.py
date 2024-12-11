from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from docling.document_converter import DocumentConverter
from haystack import Document, component
from haystack.dataclasses import ByteStream


@component
class DoclingDocumentConverter:
    SUPPORTED_OUTPUT_FORMATS = ['json']

    def __init__(self, output_format=None, temp_conversion_file_path=None):
        if output_format not in self.SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(f"Only the following output formats are currently supported: {self.SUPPORTED_OUTPUT_FORMATS}.")

        self.output_format = output_format
        self.temp_conversion_file_path = temp_conversion_file_path

    @component.output_types(documents=List[Document])
    def run(self, sources: List[Union[str, Path, ByteStream]], meta: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None):
        # TODO: handle metadata as well

        documents = []
        converter = DocumentConverter()

        for source in sources:
            docling_document = converter.convert(source)

            if self.output_format == 'json':
                # as of now, docling does not support JSON (de-)serialization to/from string,
                # hence we have to store an intermediate file
                docling_document.save_to_json(Path(self.temp_conversion_file_path))
                with open(self.temp_conversion_file_path, "w") as f:
                    new_document = Document(content=f.read())

            documents.append(new_document)

        return {"documents": documents}
