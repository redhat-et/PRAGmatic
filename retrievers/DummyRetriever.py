from retriever import Retriever


class DummyRetriever(Retriever):
    """
    For debugging only.
    """
    def __init__(self):
        self.__docs = [
            "This is a sample document.",
            "This is another document.",
            "This is one more document."
        ]

    def retrieve(self, query):
        return self.__docs
