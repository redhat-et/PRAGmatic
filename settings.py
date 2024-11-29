DEFAULT_SETTINGS = {
    # basic settings
    "vector_db_type": "milvus",
    "retriever_type": "dense",
    "embedding_model": "sentence-transformers/all-MiniLM-L12-v2",

    # Milvus-related settings
    "milvus_deployment_type": "lite",
    "milvus_file_path": "./milvus.db",
    "milvus_server_url": "http://milvus-service:19530",
    "drop_old_collection": True,

    # LLM-related settings
    "llm": "mistralai/Mistral-7B-Instruct-v0.2",
    "vllm_base_url": "http://vllm-service:8000/v1",

    # chunking options
    "chunking_method": "simple",
    "split_by": "word",
    "split_length": 1000,
    "split_overlap": 50,
    "split_threshold": 100,

    # advanced RAG options
    "top_k": 1,
    "cleaner_enabled": False,
    "ranker_enabled": False,


    # example config only from this point on

    "elasticsearch_host_url": "http://elasticsearch-service:9200",
    "elasticsearch_user": "elastic",
    "elasticsearch_password": "Q8eMMXnh0qM2kcIziDUa",
    "elasticsearch_index_name": "test_index",

    "ranking_model": "BAAI/bge-reranker-base",
}
