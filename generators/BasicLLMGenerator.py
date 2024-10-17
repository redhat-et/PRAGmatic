from langchain_community.llms import VLLM
from langchain_core.messages import HumanMessage

from generator import Generator


class BasicLLMGenerator(Generator):

    BASE_RAG_PROMPT = """You are an assistant for question-answering tasks. 

    Here is the context to use to answer the question:
    
    {context} 
    
    Think carefully about the above context. 
    
    Now, review the user question:
    
    {question}
    
    Provide an answer to this questions using only the above context. 
    
    Answer:
    """

    def __init__(self, model_name, model_parameters):
        self.__llm = VLLM(model=model_name, **model_parameters)

    def generate(self, query, context):
        rag_prompt_formatted = self.BASE_RAG_PROMPT.format(context=context, question=query)
        generation = self.__llm.invoke([HumanMessage(content=rag_prompt_formatted)])
        return generation.content
