from contexter import Contexter


class BasicContexter(Contexter):
    def create_context(self, query, documents):
        return "\n\n".join(documents)
