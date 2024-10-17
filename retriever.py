class Retriever(object):
    """
    An abstract class representing a method for retrieving documents for RAG.
    """
    def retrieve(self, query):
        raise NotImplementedError()
