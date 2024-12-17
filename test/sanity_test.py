from docling.datamodel.base_models import InputFormat

import os
from pathlib import Path
import requests

from docling.document_converter import DocumentConverter

from paragon import index_path_for_rag, execute_rag_query

SOURCE_PDF_URLS = [
    "https://docs.redhat.com/en/documentation/red_hat_build_of_microshift/4.12/pdf/cli_tools/Red_Hat_build_of_MicroShift-4.12-CLI_tools-en-US.pdf",
    "https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2-latest/pdf/introduction_to_red_hat_openshift_ai/Red_Hat_OpenShift_AI_Self-Managed-2-latest-Introduction_to_Red_Hat_OpenShift_AI-en-US.pdf",
    "https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2-latest/pdf/introduction_to_red_hat_openshift_ai/Red_Hat_OpenShift_AI_Self-Managed-2-latest-Introduction_to_Red_Hat_OpenShift_AI-en-US.pdf",
]
DOCS_LOCAL_DIR_NAME = "docs"

# True to convert PDFs to JSONs as a part of Paragon's indexing pipeline and False to do it externally
TEST_PDF_TO_JSON_CONVERSION = False

def docling_convert(docs):
    if len(os.listdir(DOCS_LOCAL_DIR_NAME)) > 0:
        # documents already converted - nothing to be done
        print("Documents are already converted - nothing to be done, will proceed to indexing the vector db \n")
        return
    print("Fetching the PDF documents provided and converting them into JSON format using Docling \n")
    converter = DocumentConverter(allowed_formats=[InputFormat.PDF])
    for doc_url in docs:
        base_output_path = os.path.join(DOCS_LOCAL_DIR_NAME, doc_url.split('/')[-1])
        if TEST_PDF_TO_JSON_CONVERSION:
            response = requests.get(doc_url)
            with open(base_output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            result = converter.convert(doc_url)
            result.document.save_as_json(Path(base_output_path + ".json"))
    print("Successfully converted the documents and saved as JSON in local directory specified \n")

def main():
    # download and convert source PDF documents to JSON format using docling
    print("Step 1: Documents specified will be fetched and converted into JSON using Docling (if not already done) \n")
    docling_convert(SOURCE_PDF_URLS)

    # index the JSONs under a Milvus Lite instance
    print("Step 2: Embedding the JSONs and indexing them into Milvus vector database \n")
    index_path_for_rag(DOCS_LOCAL_DIR_NAME,
                       milvus_deployment_type="lite",
                       milvus_file_path="./milvus.db",
                       embedding_model="sentence-transformers/all-MiniLM-L12-v2",
                       document_input_format='pdf' if TEST_PDF_TO_JSON_CONVERSION else 'json')

    # execute a simple RAG query
    print("Step 3: Executing simple RAG queries \n")
    print("Question: How to install OpenShift CLI on macOS?")
    result1 = execute_rag_query("How to install OpenShift CLI on macOS?",
                               milvus_file_path="./milvus.db",
                               embedding_model="sentence-transformers/all-MiniLM-L12-v2",
                               llm_base_url="http://vllm-service:8000/v1",
                               top_k=3)
    print("Response generated:")
    print(f"\n{result1}")
    print("\n")
    print("Question: What are the two deployment options in OpenShift AI?")
    result2 = execute_rag_query("What are the two deployment options in OpenShift AI?",
                               milvus_file_path="./milvus.db",
                               embedding_model="sentence-transformers/all-MiniLM-L12-v2",
                               llm_base_url="http://vllm-service:8000/v1",
                               top_k=3)
    print("Response generated:")
    print(f"\n{result2}")


if __name__ == '__main__':
    main()
