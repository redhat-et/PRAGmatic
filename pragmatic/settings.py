# from haystack_integrations.components.evaluators.ragas import RagasMetric
from haystack.utils import Secret
from sentence_transformers.training_args import BatchSamplers

DEFAULT_SETTINGS = {
    # basic settings
    "vector_db_type": "milvus",
    "retriever_type": "dense",
    "embedding_model_path": "sentence-transformers/all-MiniLM-L12-v2", #"./cache/finetuned_embedding-final",

    # document conversion-related settings
    "apply_docling": False,
    "docling_tokenizer_model": "sentence-transformers/all-MiniLM-L12-v2",
    "input_document_formats": ["json"],


    # Milvus-related settings
    "milvus_deployment_type": "lite",
    "milvus_file_path": "./milvus.db",
    "milvus_server_url": "http://milvus-service:19530",
    "milvus_auth_token": None,   # use Secret.from_env_var("MILVUS_TOKEN_ENV_VAR_NAME") to enable authentication
    "milvus_drop_old_collection": True,
    "milvus_connection_timeout": None,
    "milvus_collection_name": "PragmaticCollection",

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
    # this parameter is a hack to enable docling-based chunking of documents converted via docling externally
    "converted_docling_document_format": "json",

    # LLM-related settings
    "llm": "mistralai/Mistral-7B-Instruct-v0.2",
    "llm_base_url": "http://127.0.0.1:8000/v1",
    "llm_api_key": Secret.from_token("VLLM-PLACEHOLDER-API-KEY"),  # use Secret.from_env_var("API_KEY_ENV_VAR_NAME") to enable authentication
    "llm_connection_timeout": 30,
    "llm_connection_max_retries": 3,
    "llm_system_prompt": None,
    "llm_organization": None,
    "llm_response_max_tokens": 512,
    "llm_temperature": 1,
    "llm_top_p": 1,
    "llm_num_completions": 1,
    "llm_stop_sequences": None,
    "llm_frequency_penalty": 0.0,
    "llm_presence_penalty": 0.0,
    "llm_logit_bias": None,
    "llm_http_client": None,
    "generator_object": None,  # an instance of a Haystack-compatible generator object

    "enable_response_streaming": False,
    'streaming_timeout': 30, # Default timeout is 60 seconds if not specified

    # advanced RAG options
    "top_k": 1,
    "cleaner_enabled": False,
    "ranker_enabled": False,

    # embedding model fine-tuning settings
    "finetune_embedding_model": False,
    "initial_embedding_model_path": "sentence-transformers/all-MiniLM-L12-v2",
    "embedding_model_finetuning_dataset_path": "sentence-transformers/all-nli",
    "embedding_model_finetuning_dataset_subset_name": "pair-score",
    "embedding_model_finetuning_parameters": {
        "num_train_epochs": 1,
        "per_device_train_batch_size": 16,
        "warmup_ratio": 0.1,
        "learning_rate": 2e-5,
        "lr_scheduler_type": "cosine",
        "optim": "adamw_torch_fused",
        "batch_sampler": BatchSamplers.NO_DUPLICATES,
        "save_strategy": "epoch",
        "save_total_limit": 2,
        "logging_steps": 100,
    },


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
