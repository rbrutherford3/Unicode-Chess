#!/bin/python3

import os


class Turnstile:
    site_key = os.environ.get("TURNSTILE_SITE_KEY", "")
    secret_key = os.environ.get("TURNSTILE_SECRET", "")
    # Comma-separated allowlist of frontend hostnames expected in siteverify's response, per deployment.
    hostnames = {
        hostname.strip()
        for hostname in os.environ.get("TURNSTILE_HOSTNAMES", "").split(",")
        if hostname.strip()
    }
