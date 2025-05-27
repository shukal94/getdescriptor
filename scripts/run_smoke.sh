#!/usr/bin/bash

echo Running smoke tests
pytest -m smoke tests/
