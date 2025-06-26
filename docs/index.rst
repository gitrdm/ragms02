.. RAG LLM Interface Service & File-Watcher Sidecar documentation master file
   
Welcome to the RAG LLM Interface Service & File-Watcher Sidecar documentation!
===============================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   api
   design/file-watcher-sdd
   adr/index


Project Overview
----------------

This project provides a local microservice and file-watcher sidecar for enhanced, context-aware LLM responses. It supports project/tag isolation, hybrid ingestion (full and incremental), robust API design, LLM routing, and is extensible for future multi-user or production scenarios.


Usage
-----

.. include:: usage.rst


API Reference
-------------

.. include:: api.rst


File/Directory Exclusion and Ignore Patterns
---------------------------------------------

The system supports robust exclusion of files and directories from ingestion and watching using a shared `.ragignore` file (gitignore-style). See the SDD and usage documentation for details on how to configure and use this feature for both real-time and batch ingestion.

- See `examples/ignore_utils.py` for the shared ignore logic.
- See `examples/watch_with_ragignore.py` for a watcher example using `.ragignore`.
- See `examples/bulk_ingest.py` for a bulk ingestion example using `.ragignore`.

---
