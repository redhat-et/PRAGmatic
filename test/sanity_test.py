import os
from pathlib import Path

from docling.document_converter import DocumentConverter

from paragon import index_path_for_rag, execute_rag_query

SOURCE_PDF_URLS = [
    "https://docs.redhat.com/en/documentation/red_hat_build_of_microshift/4.12/pdf/cli_tools/Red_Hat_build_of_MicroShift-4.12-CLI_tools-en-US.pdf",
    "https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2.15/pdf/introduction_to_red_hat_openshift_ai/Red_Hat_OpenShift_AI_Self-Managed-2.15-Introduction_to_Red_Hat_OpenShift_AI-en-US.pdf",
    "https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2.15/pdf/getting_started_with_red_hat_openshift_ai_self-managed/Red_Hat_OpenShift_AI_Self-Managed-2.15-Getting_started_with_Red_Hat_OpenShift_AI_Self-Managed-en-US.pdf",
]
DOCS_LOCAL_DIR_NAME = "docs"

def docling_convert(docs):
    converter = DocumentConverter()
    for doc_url in docs:
        result = converter.convert(doc_url)
        output_path = os.path.join(DOCS_LOCAL_DIR_NAME, doc_url.split('/')[-1] + ".json")
        result.document.save_as_json(Path(output_path))

def main():
    # download and convert source PDF documents to JSON format using docling
    docling_convert(SOURCE_PDF_URLS)

    # index the JSONs under a Milvus Lite instance
    index_path_for_rag(DOCS_LOCAL_DIR_NAME,
                       milvus_deployment_type="lite",
                       milvus_file_path="./milvus.db",
                       embedding_model="sentence-transformers/all-MiniLM-L12-v2")

    # execute a simple RAG query
    result = execute_rag_query("How to install OpenShift CLI on macOS?",
                               milvus_file_path="./milvus.db",
                               embedding_model="sentence-transformers/all-MiniLM-L12-v2",
                               vllm_base_url="http://vllm-service:8000/v1",
                               top_k=5)
    print(result)


if __name__ == '__main__':
    main()
