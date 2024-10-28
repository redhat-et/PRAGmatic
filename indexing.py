from haystack.components.fetchers import LinkContentFetcher
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.converters import HTMLToDocument
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.writers import DocumentWriter

from settings import DEFAULT_SETTINGS

def run_indexing_pipeline(settings=DEFAULT_SETTINGS):
    document_store = ElasticsearchDocumentStore(host=settings["elasticsearch_host"],
                                                port=settings["elasticsearch_port"],
                                                username=settings["elasticsearch_username"],
                                                password=settings["elasticsearch_password"],
                                                index=settings["elasticsearch_index_name"],
                                                scheme="http")

    fetcher = LinkContentFetcher()
    converter = HTMLToDocument()

    cleaner = DocumentCleaner()
    splitter = DocumentSplitter()
    doc_embedder = SentenceTransformersDocumentEmbedder(model=settings["embedding_model"])
    writer = DocumentWriter(document_store)

    pipeline = Pipeline()
    pipeline.add_component("fetcher", fetcher)
    pipeline.add_component("converter", converter)
    pipeline.add_component("cleaner", cleaner)
    pipeline.add_component("splitter", splitter)
    pipeline.add_component("doc_embedder", doc_embedder)
    pipeline.add_component("writer", writer)

    pipeline.connect("fetcher", "converter")
    pipeline.connect("converter", "cleaner")
    pipeline.connect("cleaner", "splitter")
    pipeline.connect("splitter", "doc_embedder")
    pipeline.connect("doc_embedder", "writer")

    pipeline.run({"fetcher": {"urls": settings["urls"]}})
