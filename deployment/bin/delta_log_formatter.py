import logging
import datetime

class DeltaTimeFormatter(logging.Formatter):
    def format(self, record):
        duration = datetime.datetime.utcfromtimestamp(record.relativeCreated / 1000)
        record.delta = duration.strftime("%H:%M:%S")
        return super().format(record)

# add custom formatter to root logger
handler = logging.StreamHandler()
LOGFORMAT = '+%(delta)s - %(asctime)s - %(module)s %(levelname)-9s: %(message)s'
fmt = DeltaTimeFormatter(LOGFORMAT)
handler.setFormatter(fmt)
logging.getLogger().addHandler(handler)
