from flask import Flask
from influxdb_client import WriteApi, QueryApi


class CustomFlask(Flask):
    write_api: WriteApi
    query_api: QueryApi
