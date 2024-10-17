class Generator(object):
    """
    An abstract class wrapping the generation stage of the RAG solution (typically invoking an LLM).
    """
    def generate(self, query, context):
        raise NotImplementedError()
