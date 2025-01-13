# from haystack_integrations.components.evaluators.ragas import RagasMetric

DEFAULT_SETTINGS = {
    # basic settings
    "vector_db_type": "milvus",
    "retriever_type": "dense",
    "retrieval_embedding_model": "sentence-transformers/all-MiniLM-L12-v2",

    # document conversion-related settings
    "apply_docling": False,
    "docling_tokenizer_model": "sentence-transformers/all-MiniLM-L12-v2",
    "input_document_formats": ["json"],


    # Milvus-related settings
    "milvus_deployment_type": "lite",
    "milvus_file_path": "./milvus.db",
    "milvus_server_url": "http://milvus-service:19530",
    "drop_old_collection": True,

    # chunking options
    "chunking_enabled": True,
    "chunking_method": "docling",
    "max_tokens_per_chunk": 512,
    "split_by": "word",
    "split_length": 200,
    "split_overlap": 20,
    "split_threshold": 20,

    # other indexing-related settings
    "process_input_recursively": True,

    # LLM-related settings
    "llm": "mistralai/Mistral-7B-Instruct-v0.2",
    "llm_base_url": "http://vllm-service:8000/v1",

    # advanced RAG options
    "top_k": 1,
    "cleaner_enabled": False,
    "ranker_enabled": False,

    # evaluation metrics
    "eval_documents_path": "./docs",
    "eval_questions_answers_path": "./qa.txt",
    "eval_ragas_metrics": {
        #RagasMetric.FAITHFULNESS: {
        #    "params": None,
        #    "required_data": ['questions', 'contexts', 'responses'],
        #},
        #RagasMetric.ANSWER_CORRECTNESS: {
        #    "params": {"weights": [0.5, 0.2]},
        #    "required_data": ['questions', 'ground_truths', 'responses'],
        #},
    },


    # example config only from this point on

    "elasticsearch_host_url": "http://elasticsearch-service:9200",
    "elasticsearch_user": "elastic",
    "elasticsearch_password": "Q8eMMXnh0qM2kcIziDUa",
    "elasticsearch_index_name": "test_index",

    "ranking_model": "BAAI/bge-reranker-base",
}
