import logging
import os
import zipfile
from urllib import request
import findspark
from pyspark import SparkContext


class Spark:
    def __init__(self, host, appname, es_hadoop_ver, port=7077):
        """
        Connect to the Spark master
        """
        try:
            # findspark.init(spark_home='/usr/local/spark')
            self.__es_hadoop_ver = es_hadoop_ver
            self.__install_elastic_hadoop()
            self.__sparkcontext = SparkContext(master=f'spark://{host}:{port}', appName=appname)
            logging.info('Connected to Spark!')
        except Exception as e:
            logging.error(f'Error connecting to Spark: {e}')

    def load_index(self, indexname):
        ...

    def __install_elastic_hadoop(self):
        if f'elasticsearch-hadoop-{self.__es_hadoop_ver}' not in os.listdir('.'):
            # Download archived version of library
            logging.info(
                f'-> Elasticsearch-hadoop-{self.__es_hadoop_ver} is not installed, downloading now ...'
            )
            request.URLopener().retrieve(
                f'https://artifacts.elastic.co/downloads/elasticsearch-hadoop/elasticsearch-hadoop-{self.__es_hadoop_ver}.zip',
                "es-hadoop.zip")

            # Unzip library
            logging.info('-> Unzipping downloaded file ...')
            with zipfile.ZipFile("es-hadoop.zip", "r") as es_zip:
                es_zip.extractall()
            logging.info(f'-> Finished installing Elasticsearch-hadoop-{self.__es_hadoop_ver}!')
        else:
            logging.info(f'Elasticsearch-hadoop-{self.__es_hadoop_ver} is already installed!')

    def __del__(self):
        """
        Destroy self
        """
        self.__sparkcontext.stop()
