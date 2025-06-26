Usage
=====

Quick Start
-----------

.. code-block:: bash

   git clone <repo-url>
   cd ragms02
   make install
   make run

Open http://localhost:8000/docs for the API docs (Swagger UI).

Development Workflow
--------------------

- Use `make test` to run all tests.
- Use `make lint` and `make format` for code quality.
- Use `make docs` to build this documentation.

Configuration
-------------

- See `README.md` and `docs/design/file-watcher-sdd.md` for configuration options.

File/Directory Exclusion and Ignore Patterns
---------------------------------------------

Both the file-watcher sidecar and bulk ingestion scripts support robust exclusion of files and directories using a shared `.ragignore` file. This file uses `.gitignore`-style syntax and can be customized per project. The ignore logic is implemented using the `pathspec` library and a shared utility, ensuring that both real-time and batch ingestion respect the same patterns.

- On startup, the watcher loads `.ragignore` and applies the patterns to all file system events.
- Bulk ingestion scripts also load `.ragignore` and skip ignored files/directories during recursive scans.
- Patterns can be customized to exclude any files, directories, or file types as needed.

See `examples/ignore_utils.py` and `examples/watch_with_ragignore.py` for implementation details.
