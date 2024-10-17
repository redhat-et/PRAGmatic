import time

import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers

from settings import DEFAULT_SETTINGS


def scrape_openshift_docs(base_url, doc_urls):
    """
    Scrapes the OpenShift documentation from the given list of URLs..
    """
    documents = []

    for url in doc_urls:
        full_url = f"{base_url}{url}"
        response = requests.get(full_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the title and content (Assuming OpenShift docs have title and content in these tags)
            title = soup.find('title').get_text()
            content = soup.find('body').get_text()  # You may need to adjust this depending on the HTML structure

            documents.append({
                "title": title.strip(),
                "content": content.strip(),
                "url": full_url
            })
        else:
            print(f"Failed to retrieve {full_url}")

    # To avoid overwhelming the server, let's wait a bit between requests
    time.sleep(1)

    return documents

def create_index(es_host, index_name):
    """
    Creates an empty Elasticsearch index with appropriate settings and mappings.
    """
    es = Elasticsearch([es_host])

    # Define the index settings and mappings
    settings = {
        "settings": {
            "number_of_shards": 1,  # For simplicity, we are using one shard
            "number_of_replicas": 0  # No replicas in a local setup
        },
        "mappings": {
            "properties": {
                "content": {
                    "type": "text"  # Content field where documents will be stored
                },
                "title": {
                    "type": "text"  # Optional: A title field for the document
                },
                "url": {
                    "type": "keyword"
                }
            }
        }
    }

    # Create the index
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=settings)
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")


def populate_index(es_host, index_name, documents):
    """
    Populates the Elasticsearch index with a set of documents.
    """
    es = Elasticsearch([es_host])

    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in documents
    ]

    helpers.bulk(es, actions)
    print(f"Documents indexed successfully into '{index_name}'.")


if __name__ == "__main__":

    # Create the index
    create_index(DEFAULT_SETTINGS["elasticsearch_host_url"], DEFAULT_SETTINGS["elasticsearch_index_name"])

    base_url = "https://docs.openshift.com/container-platform/4.17/"
    # For now, we just index a small, semi-random list of documents. A better solution will be provided later.
    doc_urls = [
        "installing/installing_faq.html",
        "cli_reference/openshift_cli/getting-started-cli.html",
        "architecture/architecture-installation.html",
        "administration/understanding-networking.html",
        "installing/installing_bare_metal/installing-bare-metal.html",
        "security/container_security/container-security.html",
        "scalability_and_performance/understanding-auto-scaling.html",
        "developers/application_life_cycle_management/understanding-alm.html",
        "serverless/serverless-architecture.html",
        "backup_and_restore/disaster_recovery.html",
        "installing/installing-azure/installing-azure.html",
        "installing/installing_gcp/installing-gcp.html",
        "logging/cluster-logging-deploying.html",
        "logging/cluster-logging-collector.html",
        "networking/network_policy/about-network-policy.html",
        "developers/cli-guide/cli-guide-projects.html",
        "nodes/clusters/nodes.html",
        "nodes/scheduling/nodes-scheduling.html",
        "authentication/understanding-authentication.html",
        "security/understanding-security-context-constraints.html",
        "scalability_and_performance/scaling-cluster.html",
        "architecture/control-plane.html",
        "developers/application_life_cycle_management/working-with-apps.html",
        "administration/about-machine-sets.html",
        "openshift_images/using-images.html"
    ]
    documents_to_index = scrape_openshift_docs(base_url, doc_urls)

    # Populate the index with documents
    populate_index(DEFAULT_SETTINGS["elasticsearch_host_url"],
                   DEFAULT_SETTINGS["elasticsearch_index_name"], documents_to_index)
