from docling.datamodel.base_models import InputFormat

import os
from pathlib import Path
import requests

from docling.document_converter import DocumentConverter

from paragon import index_path_for_rag, execute_rag_query


SOURCE_PDF_URLS = [
    "https://docs.redhat.com/en/documentation/red_hat_build_of_microshift/4.12/pdf/cli_tools/Red_Hat_build_of_MicroShift-4.12-CLI_tools-en-US.pdf",
    "https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2.15/pdf/introduction_to_red_hat_openshift_ai/Red_Hat_OpenShift_AI_Self-Managed-2.15-Introduction_to_Red_Hat_OpenShift_AI-en-US.pdf",
    "https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2.15/pdf/getting_started_with_red_hat_openshift_ai_self-managed/Red_Hat_OpenShift_AI_Self-Managed-2.15-Getting_started_with_Red_Hat_OpenShift_AI_Self-Managed-en-US.pdf",
]
DOCS_LOCAL_DIR_NAME = "docs"

# True to convert PDFs to JSONs as a part of Paragon's indexing pipeline and False to do it externally
TEST_PDF_TO_JSON_CONVERSION = True

def docling_convert(docs):
    if len(os.listdir(DOCS_LOCAL_DIR_NAME)) > 0:
        # documents already converted - nothing to be done
        return
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

def main():
    # download and convert source PDF documents to JSON format using docling
    docling_convert(SOURCE_PDF_URLS)

    # index the JSONs under a Milvus Lite instance
    index_path_for_rag(DOCS_LOCAL_DIR_NAME,
                       milvus_deployment_type="lite",
                       milvus_file_path="./milvus.db",
                       embedding_model="sentence-transformers/all-MiniLM-L12-v2",
                       document_input_format='pdf' if TEST_PDF_TO_JSON_CONVERSION else 'json')

    # execute a simple RAG query
    result = execute_rag_query("How to install OpenShift CLI on macOS?",
                               milvus_file_path="./milvus.db",
                               embedding_model="sentence-transformers/all-MiniLM-L12-v2",
                               vllm_base_url="http://vllm-service:8000/v1",
                               top_k=5)
    print(f"\n\n\n{result}")


if __name__ == '__main__':
    main()
