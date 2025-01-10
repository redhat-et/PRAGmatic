from setuptools import setup, find_packages

setup(
    name='pragmatic',
    version='0.1.0',
    packages=find_packages(),
    description='An experimental RAG framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/redhat-et/PRAGmatic'
)
