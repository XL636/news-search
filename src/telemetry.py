"""OpenTelemetry instrumentation for InsightRadar."""

import logging

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

logger = logging.getLogger(__name__)

_initialized = False


def setup_telemetry(app) -> None:
    """Configure OpenTelemetry tracing and instrument FastAPI.

    Uses ConsoleSpanExporter for development. Can be swapped for
    OTLPSpanExporter when a collector (Jaeger/Tempo) is available.
    """
    global _initialized
    if _initialized:
        return

    resource = Resource.create({"service.name": "insightradar", "service.version": "0.20.0"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)

    _initialized = True
    logger.info("OpenTelemetry tracing initialized (ConsoleSpanExporter)")
