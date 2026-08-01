---
title: "FastAPI Introduction"
date: "2026-08-01"
author: "pkm"
last_audited: "2026-08-01"
tags: [fastapi]
status: permanent
aliases: []
sources: ["https://fastapi.tiangolo.com"]
references: []
---

# FastAPI Introduction

## Summary

FastAPI is a modern Python web framework for building APIs. It is designed to be fast both to build and to run and easy to learn, with the goal of expressing common API patterns in minimal code. Built on standards such as OpenAPI and JSON Schema, FastAPI generates an interactive API documentation interface automatically and offers async support through Python's async and await syntax.

## Notes

FastAPI was released in 2018 by Sebastián Ramírez as an open-source framework aimed at developers who want standards-based Python APIs built on type hints, with editor-friendly tooling and automatic API documentation out of the box.

Its main characteristics include:

- Type hints and automatic data validation. Declared types in Python function signatures drive request validation, serialization, and editor support (validation and serialization are handled via Pydantic).
- Native async and await support enables concurrency for I/O-bound operations, while synchronous (`def`) endpoints still work by running in a threadpool.
- Automatic generation of interactive API documentation. FastAPI auto-generates the OpenAPI schema, with Swagger UI served at `/docs` and ReDoc at `/redoc`.
- High performance on an ASGI stack. FastAPI is built on Starlette and runs on an ASGI server (e.g. Uvicorn); end-to-end performance depends on both the framework and the server.
- Standards-based design built directly on OpenAPI and JSON Schema for API and data modelling.

FastAPI is commonly used for building REST APIs, backend services, and microservices. It is suited to projects that need rapid development combined with validated, self-documented interfaces.

## References

[FastAPI](https://fastapi.tiangolo.com)

## Changelog

- 2026-08-01: Note created.
- 2026-08-01: Added author, precise API documentation endpoints (/docs, /redoc), Starlette+ASGI-server performance attribution, sources metadata.
- 2026-08-01: Tightened async bullet (sync endpoints run in a threadpool); trimmed redundant API documentation phrasing.
- 2026-08-01: Renamed to fastapi-introduction.md; aligned H1 with title and filename; removed Summary/Notes redundancy.
