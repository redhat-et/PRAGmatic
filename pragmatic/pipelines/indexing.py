import os

from docling.chunking import HybridChunker
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument, TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter

from docling_haystack.converter import DoclingConverter, ExportType

from pragmatic.haystack.docling_splitter import DoclingDocumentSplitter
from pragmatic.pipelines.pipeline import CommonPipelineWrapper


class IndexingPipelineWrapper(CommonPipelineWrapper):

    def _add_cleaner(self):
        if not self._settings["cleaner_enabled"]:
            return
        cleaner = DocumentCleaner()
        self._add_component("cleaner", cleaner)

    def _add_splitter(self):
        if not self._settings["chunking_enabled"]:
            return
        splitter_type = self._settings["chunking_method"].lower()
        if splitter_type == "simple":
            splitter = DocumentSplitter(split_by=self._settings["split_by"],
                                        split_length=self._settings["split_length"],
                                        split_overlap=self._settings["split_overlap"],
                                        split_threshold=self._settings["split_threshold"])
        elif splitter_type == "docling":
            if self._settings["apply_docling"]:
                # when docling is used, chunking is handled in the respective converter component
                return
            splitter = DoclingDocumentSplitter(embedding_model_id=self._settings["docling_tokenizer_model"],
                                               content_format=self._settings["converted_docling_document_format"],
                                               max_tokens=self._settings["max_tokens_per_chunk"])
        else:
            raise ValueError(f"Unsupported chunking method: {splitter_type}")

        self._add_component("splitter", splitter)

    def _add_embedder(self):
        embedder = SentenceTransformersDocumentEmbedder(model=self._settings["embedding_model"])
        self._add_component("embedder", embedder)

    def _add_writer(self):
        document_store = self._init_document_store(retrieval_mode=False)
        writer = DocumentWriter(document_store)
        self._add_component("writer", writer)

    def build_pipeline(self):
        self._add_fetcher()
        self._add_converter()
        self._add_cleaner()
        self._add_splitter()
        self._add_embedder()
        self._add_writer()

    def _add_fetcher(self):
        raise NotImplementedError()

    def _add_converter(self):
        raise NotImplementedError()


class RemoteHTMLIndexingPipelineWrapper(IndexingPipelineWrapper):
    def __init__(self, settings, urls):
        super().__init__(settings)
        self._urls = urls

    def _add_fetcher(self):
        fetcher = LinkContentFetcher()
        self._add_component("fetcher", fetcher, component_args={"urls": self._urls})

    def _add_converter(self):
        converter = HTMLToDocument()
        self._add_component("converter", converter)


class LocalFileIndexingPipelineWrapper(IndexingPipelineWrapper):
    def __init__(self, settings, doc_path):
        super().__init__(settings)

        self._source_files = []

        if self._settings['process_input_recursively']:
            for root, _, files in os.walk(doc_path):
                for file in files:
                    self.__verify_and_add_input_file(root, file)
        else:
            for file in os.listdir(doc_path):
                self.__verify_and_add_input_file(doc_path, file)

    def __verify_and_add_input_file(self, root_path, file_path):
        absolute_path = os.path.abspath(os.path.join(root_path, file_path))
        if not os.path.isfile(absolute_path):
            return False
        if self._settings['input_document_formats'] is not None and self._settings['input_document_formats'] != '*':
            file_extension = absolute_path.split('.')[-1]
            if file_extension not in self._settings['input_document_formats']:
                return False
        self._source_files.append(absolute_path)
        return True

    def _add_fetcher(self):
        return

    def _add_converter(self):
        if self._settings["apply_docling"]:
            use_docling_chunker = self._settings["chunking_enabled"] and self._settings["chunking_method"].lower() == 'docling'
            export_type = ExportType.DOC_CHUNKS if use_docling_chunker else ExportType.MARKDOWN
            converter = DoclingConverter(export_type=export_type,
                                         chunker=HybridChunker(tokenizer=self._settings['docling_tokenizer_model']))
            converter_args = {"paths": self._source_files}
        else:
            converter = TextFileToDocument()
            converter_args = {"sources": self._source_files}
        self._add_component("converter", converter, component_args=converter_args)
