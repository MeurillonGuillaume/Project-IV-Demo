from elasticsearch import Elasticsearch
import logging


class Elastic:
    def __init__(self, host, port=9200):
        try:
            self.__elastic = Elasticsearch(f'http://{host}:{port}')
            logging.info('Connected to Elasticsearch!')
        except Exception as e:
            logging.error(f'Error connecting to Elasticsearch: {e}')
