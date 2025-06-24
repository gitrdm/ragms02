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
