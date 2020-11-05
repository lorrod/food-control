""" Project settings file """


class Config(object):
	HOST = 'localhost'
	PORT = 5000
	THREADED = 'True'				# Allows multithreading.
	DEBUG = True					# Debug mode. Do not allow in production.
	SEND_FILE_MAX_AGE_DEFAULT = 0
	MONGO_URI = "mongodb://"    # !
	TG_TOKEN = ""               # !
	WEBHOOK_HOST = ''           # !
	WEBHOOK_PORT = 8443
	WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
	WEBHOOK_URL_PATH = "/%s/" % (TG_TOKEN)
	WEBHOOK_LISTEN = '0.0.0.0'
	WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
	WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key
