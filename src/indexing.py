import os

from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument, JSONConverter
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter

from pipeline import CommonPipelineWrapper


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
            splitter = None  # TODO: implement docling-specific splitting
        else:
            raise ValueError(f"Unsupported chunking method: {splitter_type}")

        self._add_component("splitter", splitter)

    def _add_writer(self):
        document_store = self._init_document_store()
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


class LocalJSONIndexingPipelineWrapper(IndexingPipelineWrapper):
    def __init__(self, settings, doc_path):
        super().__init__(settings)

        self._json_files = []
        for file in os.listdir(doc_path):
            file_path = os.path.join(doc_path, file)
            if os.path.isfile(file_path) and file.endswith(".json"):
                self._json_files.append(os.path.abspath(file_path))

    def _add_fetcher(self):
        return

    def _add_converter(self):
        converter = JSONConverter()
        self._add_component("converter", converter, component_args={"sources": self._json_files})
