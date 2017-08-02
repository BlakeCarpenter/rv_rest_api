import mysql.connector
from mysql_config import mysql_config

def db_connect():
	return mysql.connector.connect(**mysql_config)

def db_cursor(connection):
	return connection.cursor(buffered=True)