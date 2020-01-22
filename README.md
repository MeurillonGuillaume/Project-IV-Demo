# About this repository

This repository contains a Flask application which is used as Demo application for Project-IV.

## 1. Application use

This application has been made to easilly query both the Elasticsearch cluster and Apache Spark standalone-cluster I have set up for Project-IV.

### 1.1 Elasticsearch

Elasticsearch can be queried using either the preferred **DSL** queries, or **SQL** queries. SQL-queries are included to show that Spark and Elasticsearch queries can be interchangeable.

### 1.2 Apache Spark

Apache Spark can be queried only using **SparkSQL**, since DataFrame operations aren't that simple to create a simple webapp for.

### 1.3 Performance testing

To show the performance of both systems, several items are included in the webapp:

1. **Grafana graphs**: These graphs display the current resource usage for each active node, both Elasticsearch and Apache Spark
2. **Response time**: The response time block shows the time a certain query took to compute.