from retriever import Retriever
from elasticsearch import Elasticsearch


class ElasticsearchRetriever(Retriever):
    def __init__(self, es_host_url, es_index_name, top_k):
        self.__es_client = Elasticsearch([es_host_url])
        self.__es_index_name = es_index_name
        self.__top_k = top_k

    def retrieve(self, query):
        """
        Retrieves relevant documents from Elasticsearch using sparse retrieval mode (BM25).
        """
        search_query = {
            "query": {
                "match": {
                    "content": query  # Assuming 'content' is the field that holds the document text
                }
            }
        }

        response = self.__es_client.search(index=self.__es_index_name, body=search_query, size=self.__top_k)

        # Process the response and extract the documents and scores
        documents = []
        for hit in response['hits']['hits']:
            documents.append(hit['_source'])

        return documents
