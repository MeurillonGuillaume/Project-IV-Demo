from elasticsearch import Elasticsearch
import logging
import json
import requests


class Elastic:
    def __init__(self, host, port=9200):
        try:
            self.__host = host
            self.__port = port
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

    def query_sql(self, q):
        """
        Query Elasticsearch with SQL
        """
        q = str(q).replace('"', '\"')
        return json.dumps(requests.post(f'http://{self.__host}:{self.__port}/_xpack/sql?format=json&pretty=true',
                                        data=json.dumps({'query': q}),
                                        headers={
                                            'Content-type': 'application/json'
                                        }).text, indent=4)

    def query_dsl(self, querybody, index):
        """
        Query Elasticsearch using DSL queries
        """
        return json.dumps(self.__elastic.search(index=index, body=querybody), indent=4)
