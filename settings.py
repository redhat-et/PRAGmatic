DEFAULT_SETTINGS = {
    "embedding_model": "sentence-transformers/all-mpnet-base-v2",
    "ranking_model": "BAAI/bge-reranker-base",

    "llm": "ibm-granite/granite-3.0-2b-instruct",

    "elasticsearch_host_url": "localhost:9200",
    "elasticsearch_user": "elastic",
    "elasticsearch_password_file": "/app/elastic_password.log",
    "elasticsearch_index_name": "test_index",
    "elasticsearch_top_k": 1,

    "vllm_base_url": "http://localhost:8000/v1",

    "urls": [
        "https://docs.openshift.com/container-platform/4.17/installing/overview/index.html",
        "https://docs.openshift.com/container-platform/4.17/cli_reference/openshift_cli/getting-started-cli.html",
        "https://docs.openshift.com/container-platform/4.17/architecture/architecture-installation.html",
        "https://docs.openshift.com/container-platform/4.17/networking/understanding-networking.html",
        "https://docs.openshift.com/container-platform/4.17/installing/installing_bare_metal/installing-bare-metal.html",
        "https://docs.openshift.com/container-platform/4.17/security/container_security/security-understanding.html",
        "https://docs.openshift.com/container-platform/4.17/scalability_and_performance/optimization/optimizing-cpu-usage.html",
        "https://docs.openshift.com/lightspeed/1.0tp1/about/ols-about-openshift-lightspeed.html",
        "https://docs.openshift.com/container-platform/4.17/edge_computing/ztp-advanced-install-ztp.html",
        "https://docs.openshift.com/container-platform/4.17/backup_and_restore/graceful-cluster-restart.html",
        "https://docs.openshift.com/container-platform/4.17/installing/installing_azure/preparing-to-install-on-azure.html",
        "https://docs.openshift.com/container-platform/4.17/installing/installing_gcp/installing-gcp-account.html",
        "https://docs.openshift.com/container-platform/4.17/extensions/arch/components.html",
        "https://docs.openshift.com/container-platform/4.17/storage/persistent_storage/persistent-storage-aws.html",
        "https://docs.openshift.com/container-platform/4.17/cicd/index.html",
        "https://docs.openshift.com/container-platform/4.17/machine_management/machine-phases-lifecycle.html",
        "https://docs.openshift.com/container-platform/4.17/operators/understanding/olm-what-operators-are.html",
        "https://docs.openshift.com/container-platform/4.17/virt/updating/upgrading-virt.html",
        "https://docs.openshift.com/container-platform/4.17/authentication/understanding-authentication.html",
        "https://docs.openshift.com/container-platform/4.17/applications/working_with_helm_charts/odc-working-with-helm-releases.html",
        "https://docs.openshift.com/container-platform/4.17/nodes/clusters/nodes-cluster-resource-configure.html",
        "https://docs.openshift.com/container-platform/4.17/architecture/control-plane.html",
        "https://docs.openshift.com/container-platform/4.17/migrating_from_ocp_3_to_4/index.html",
        "https://docs.openshift.com/container-platform/4.17/machine_management/modifying-machineset.html",
        "https://docs.openshift.com/container-platform/4.17/openshift_images/managing_images/managing-images-overview.html"
    ],
}
