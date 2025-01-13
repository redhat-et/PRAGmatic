import os

from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument, TextFileToDocument
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter

from pragmatic.haystack.docling_converter import DoclingDocumentConverter
from pragmatic.haystack.docling_splitter import DoclingDocumentSplitter
from pragmatic.pipelines.pipeline import CommonPipelineWrapper


class IndexingPipelineWrapper(CommonPipelineWrapper):

    def _add_cleaner(self):
        if not self._settings["cleaner_enabled"]:
            return
        cleaner = DocumentCleaner()
        self._add_component("cleaner", cleaner)

    def _add_splitter(self):
        splitter_type = self._settings["chunking_method"]
        if splitter_type == "simple":
            splitter = DocumentSplitter(split_by=self._settings["split_by"],
                                        split_length=self._settings["split_length"],
                                        split_overlap=self._settings["split_overlap"],
                                        split_threshold=self._settings["split_threshold"])
        elif splitter_type == "docling":
            splitter = DoclingDocumentSplitter(embedding_model_id=self._settings["docling_embedding_model"],
                                               content_format=self._settings["document_conversion_format"],
                                               max_tokens=self._settings["max_tokens_per_chunk"])
        else:
            raise ValueError(f"Unsupported chunking method: {splitter_type}")

        self._add_component("splitter", splitter)

    def _add_embedder(self):
        embedder = SentenceTransformersDocumentEmbedder(model=self._settings["retrieval_embedding_model"])
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

        self._json_files = []

        if self._settings['process_input_recursively']:
            for root, _, files in os.walk(doc_path):
                for file in files:
                    self.__verify_and_add_input_file(root, file)
        else:
            for file in os.listdir(doc_path):
                self.__verify_and_add_input_file(doc_path, file)

    def __verify_and_add_input_file(self, root_path, file_path):
        if not os.path.isfile(file_path):
            return False
        if not file_path.endswith(f".{self._settings['document_input_format']}"):
            return False
        self._json_files.append(os.path.abspath(os.path.join(root_path, file_path)))
        return True

    def _add_fetcher(self):
        return

    def _add_converter(self):
        if self._settings["document_input_format"] == self._settings["document_conversion_format"]:
            # documents are already provided in the conversion format and there is no need to apply docling on them
            converter = TextFileToDocument()
        else:
            # we have to used docling to convert the documents to the specified format
            converter = DoclingDocumentConverter(output_format=self._settings["document_conversion_format"],
                                                 temp_conversion_file_path=self._settings["temp_conversion_file_path"])
        self._add_component("converter", converter, component_args={"sources": self._json_files})
