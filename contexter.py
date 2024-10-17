class Contexter(object):
    """
    An abstract class wrapping the process of creating RAG context from a list of retrieved documents.
    """
    def create_context(self, query, documents):
        raise NotImplementedError()
