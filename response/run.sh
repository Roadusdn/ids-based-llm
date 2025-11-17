#!/usr/bin/env bash
uvicorn response.app:app --host 0.0.0.0 --port 9001 --reload
