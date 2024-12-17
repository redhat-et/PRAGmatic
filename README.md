# PaRAGon

A **customizable, pluggable, and scalable Retrieval-Augmented Generation (RAG) framework** designed to streamline the process of building AI-powered applications that require knowledge-grounded text generation. This framework provides end-to-end components for retrieval, processing, and generation, while allowing users to plug in custom modules at every stage.

## Features

* **Pluggable Design**: Easily integrate custom modules for retrieval, preprocessing, and generation.
* **Framework-Agnostic**: Compatible with popular frameworks like LangChain, LLAMAIndex etc.
* **Customizable Pipelines**: Configure workflows tailored to your use case (e.g., question answering, summarization, etc.).
* **Scalability**: Deploy locally or in distributed cloud environments.
* **Pre-built Modules**: Includes commonly used retrieval and generation backends for quick setup.
* **Integration Friendly**: Supports REST APIs, message queues, and file-based inputs/outputs

## Default RAG Components

The default implementation of the RAG framework is designed for optimal performance with the following stack:

* **Pipeline**: [Haystack](https://github.com/deepset-ai/haystack), AI orchestration framework to build customizable, production-ready LLM applications
* **Vector Database**: [Milvus](https://github.com/milvus-io/milvus), a cloud-native vector database, storage
* **Embedding Model**: `sentence-transformers/all-MiniLM-L12-v2` pre-trained embedding model from Hugging Face for vectorization
* **LLM**: `mistral-7b-v0.1`
* **Document Parser**: [Docling](https://github.com/DS4SD/docling) parses documents and exports them to the desired format with ease and speed

## Getting Started

### Prerequisites

- `Python 3.9+`

### Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/rag-framework.git
cd rag-framework
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the RAG pipeline locally

We have a simple demo script `test/sanity_test.py` that you can run to test the RAG pipeline.

Before running the script, ensure that you update the following vars in the `paragon/settings.py` file:

- `milvus_server_url` - You can replace this with your hosted Milvus vector DB endpoint else use the default which will be an in-memory local deployment of Milvus Lite
- `llm_base_url` - The LLM serving endpoint you would like to interact with. It can either be a locally running LLM or a hosted LLM
-  `llm` - The corresponding model name of the LLM being served at the above specified URL

Optionally, you can change many other settings that are mentioned in the `paragon/settings.py` script such as `retrieval_embedding_model` for your choice of embedding model, `top_k` the number of search results you would like to be returned etc to suit your needs.

Once all the settings have been made, you can run the following:

```python
python test/sanity_test.py
```

The `test/sanity_test.py` script includes example PDFs that are processed and converted into JSON format using Docling. These JSON files are then indexed as embeddings in the Milvus vector database. The script also provides sample queries that are run through the RAG pipeline, allowing you to observe the generated responses.