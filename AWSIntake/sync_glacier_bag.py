#!/usr/bin/env python
"""
airflow workflow that:
- listens for restore requests from a specific queue. That queue was set up to notify listeners
when a glacier restore request was complete.
"""