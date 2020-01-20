from pyspark import SparkContext
import findspark
import logging


class Spark:
    def __init__(self, host, appname, port=7077):
        """
        Connect to the Spark master
        """
        try:
            findspark.init(spark_home='/usr/local/spark')
            self.__sparkcontext = SparkContext(master=f'spark://{host}:{port}', appName=appname)
            logging.info('Connected to Spark!')
        except Exception as e:
            logging.error(f'Error connecting to Spark: {e}')

    def __del__(self):
        """
        Destroy self
        """
        self.__sparkcontext.stop()
