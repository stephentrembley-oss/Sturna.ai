import logging
from typing import Optional, Dict, Any

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


class TracingService:
    """
    OpenTelemetry-based distributed tracing for Sturna.ai.
    Falls back to structured logging if OpenTelemetry is not installed.
    Supports SOC 2 / EU AI Act observability requirements.
    """

    def __init__(self, service_name: str = "sturna-ai"):
        self.service_name = service_name
        self.tracer = None

        if OTEL_AVAILABLE:
            provider = TracerProvider()
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
            self.tracer = trace.get_tracer(service_name)
        else:
            logging.getLogger(__name__).warning(
                "OpenTelemetry not installed. Falling back to basic logging."
            )

    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        if self.tracer:
            return self.tracer.start_as_current_span(name, attributes=attributes or {})
        else:
            # Fallback context manager
            from contextlib import contextmanager

            @contextmanager
            def _noop_span():
                yield None
            return _noop_span()

    def instrument_fastapi(self, app):
        if OTEL_AVAILABLE:
            FastAPIInstrumentor.instrument_app(app)
        else:
            logging.getLogger(__name__).info("Skipping FastAPI instrumentation (OpenTelemetry not available)")


# Global instance
tracing = TracingService()
