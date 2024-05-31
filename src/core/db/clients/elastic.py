from contextlib import contextmanager

from elasticsearch import Elasticsearch


@contextmanager
def elastic_search_connection(dsn: str):
    """Создает подключение к ElasticSearch, которое закроет на выходе."""
    es_connection = Elasticsearch(dsn)
    try:
        yield es_connection
    finally:
        es_connection.close()
