import logging
import os
import zipfile
from urllib import request
import pandas as pd
import findspark
import json
from pyspark import SparkContext, SQLContext


class Spark:
    def __init__(self, host, appname, es_hadoop_ver, internal_nodes, port=7077):
        """
        Connect to the Spark master
        """
        try:
            findspark.init(spark_home='/usr/local/spark')
            self.__es_hadoop_ver = es_hadoop_ver
            self.__install_elastic_hadoop()
            self.__internal_nodes = internal_nodes
            self.__sparkcontext = SparkContext(master=f'spark://{host}:{port}', appName=appname)
            self.__sqlcontext = SQLContext(self.__sparkcontext)
            logging.info('Connected to Spark!')
        except Exception as e:
            logging.error(f'Error connecting to Spark: {e}')

    def query_spark_sql(self, query):
        """
        Query the SQLContext API with SQL queries
        """
        response_rdd = self.__sqlcontext.sql(query)
        return json.dumps(response_rdd.toPandas().to_dict(orient='records'), indent=4)

    def load_index(self, indexname):
        """
        Load an Elasticsearch index
        """
        data_rdd = self.__sparkcontext.newAPIHadoopRDD(
            inputFormatClass="org.elasticsearch.hadoop.mr.EsInputFormat",
            keyClass="org.apache.hadoop.io.NullWritable",
            valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
            conf={
                # specify the node that we are reading data from
                "es.nodes": self.__internal_nodes,
                # specify the read index
                "es.resource": indexname
            })
        data_rdd = data_rdd.cache()
        df = self.__sqlcontext.createDataFrame(data_rdd)
        df.registerTempTable(indexname)

    def __install_elastic_hadoop(self):
        """
        Install the Elastic_hadoop connector
        """
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

        # Include Elastic-Hadoop in path
        os.environ[
            'PYSPARK_SUBMIT_ARGS'] = f'--jars elasticsearch-hadoop-{self.__es_hadoop_ver}/dist/elasticsearch-spark-20_2.11-{self.__es_hadoop_ver}.jar pyspark-shell'

        # Define using Python3 on the Spark server-side instead of default Python2.7
        os.environ["PYSPARK_PYTHON"] = "/usr/bin/python3"

    def __del__(self):
        """
        Destroy self
        """
        self.__sparkcontext.stop()
