"""Framework integrations for PromptRails tracing.

Each integration is imported on demand and only requires its own optional
dependency:

- ``promptrails.tracing.integrations.langchain`` — a LangChain callback handler
- ``promptrails.tracing.integrations.openai`` — wrap an OpenAI-compatible client
- ``promptrails.tracing.integrations.anthropic`` — wrap an Anthropic client
- ``promptrails.tracing.integrations.google`` — wrap a Google GenAI client
- ``promptrails.tracing.integrations.otel`` — an OpenTelemetry span exporter
"""
