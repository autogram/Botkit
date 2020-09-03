import logzero

logzero.LogFormatter.DEFAULT_FORMAT = (
    "%(color)s[%(levelname)1.1s %(asctime)s %(name)s %(module)s:%(lineno)d]%(end_color)s %("
    "message)s"
)
