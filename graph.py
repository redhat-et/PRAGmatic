from typing_extensions import TypedDict
from typing import List

from langgraph.graph import StateGraph, START, END


class GraphState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """
    query: str  # User query
    reply: str  # LLM-generated answer
    documents: List[str]  # List of retrieved documents
    context: str  # RAG context for the user query


class GraphBuilder(object):
    """
    A class for handling the graph creation process according to the parameters.
    """
    def __init__(self, retriever, contexter, generator):
        self.__retriever = retriever
        self.__contexter = contexter
        self.__generator = generator

    def __retrieve(self, state):
        return {"documents": self.__retriever.retrieve(state["query"])}

    def __create_context(self, state):
        return {"context": self.__contexter.create_context(state["query"], state["documents"])}

    def __generate(self, state):
        return {"reply": self.__generator.generate(state["query"], state["context"])}

    def create_graph(self):
        workflow = StateGraph(GraphState)

        # Define the nodes
        workflow.add_node("retrieve", self.__retrieve)
        workflow.add_node("create_context", self.__create_context)
        workflow.add_node("generate", self.__generate)

        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "create_context")
        workflow.add_edge("create_context", "generate")
        workflow.add_edge("generate", END)

        graph = workflow.compile()
        return graph
