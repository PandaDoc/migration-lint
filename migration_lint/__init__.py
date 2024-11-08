import logging

logger = logging.getLogger("default")
logger.setLevel(level=logging.DEBUG)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter("%(message)s")
fh.setFormatter(fh_formatter)
logger.addHandler(fh)
