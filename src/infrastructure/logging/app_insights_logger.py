import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

class AppInsightsHandler(logging.Handler):
    """Logging handler for Azure Application Insights."""

    def __init__(self, instrumentation_key: str):
        super().__init__()
        self.exporter = AzureLogHandler(connection_string=f'InstrumentationKey={instrumentation_key}')

    def emit(self, record: logging.LogRecord):
        # Forward the record to Azure
        self.exporter.emit(record)
