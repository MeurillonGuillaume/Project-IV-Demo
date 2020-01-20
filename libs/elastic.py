from elasticsearch import Elasticsearch
import logging


class Elastic:
    def __init__(self, host, port=9200):
        try:
            self.__elastic = Elasticsearch(f'http://{host}:{port}')
            logging.info('Connected to Elasticsearch!')
        except Exception as e:
            logging.error(f'Error connecting to Elasticsearch: {e}')

    def get_user_indices(self):
        """
        Return a list of user-created indices
        """
        idx = self.__elastic.indices.get_alias().keys()
        return [i for i in idx if i[0] is not '.']
