#!/usr/bin/env python3
"""Patch docker-compose.prod.yml to add OAuth and email env vars."""
import re

compose_path = '/home/ubuntu/sim/docker-compose.prod.yml'

with open(compose_path, 'r') as f:
    content = f.read()

# The extra env vars to add to the simstudio service
extra_vars = """      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID:-}
      - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET:-}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-}
      - RESEND_API_KEY=${RESEND_API_KEY:-}
      - GOOGLE_GENERATIVE_AI_API_KEY=${GOOGLE_GENERATIVE_AI_API_KEY:-}
      - NEXT_PUBLIC_SOCKET_URL=${NEXT_PUBLIC_SOCKET_URL:-}
      - SOCKET_SERVER_URL=${SOCKET_SERVER_URL:-http://realtime:3002}"""

# Insert after the SIM_AGENT_API_URL line
old = '      - SIM_AGENT_API_URL=${SIM_AGENT_API_URL}'
new = old + '\n' + extra_vars

if old not in content:
    print(f"ERROR: Could not find anchor line: {old}")
    print("Current content around line 22:")
    for i, line in enumerate(content.split('\n')[18:30], 19):
        print(f"  {i}: {line}")
    exit(1)

if extra_vars in content:
    print("Already patched, skipping.")
else:
    content = content.replace(old, new, 1)
    with open(compose_path, 'w') as f:
        f.write(content)
    print("Patched successfully!")

# Verify
with open(compose_path, 'r') as f:
    lines = f.readlines()

print(f"\nLines 20-30 of compose file:")
for i, line in enumerate(lines[19:30], 20):
    print(f"  {i}: {line}", end='')
