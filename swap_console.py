#!/usr/bin/env python3
"""Wait for console build to finish, then swap the image in docker-compose and restart."""
import subprocess
import time
import sys
import re

compose_path = '/home/ubuntu/appwrite/docker-compose.yml'
build_log = '/tmp/build.log'
image_name = 'forwarddb-console:latest'

print('Checking build status...')

# Check if build is done
with open(build_log) as f:
    content = f.read()

if 'DONE' in content or 'naming to docker.io' in content:
    print('Build already complete!')
elif 'error' in content.lower() and 'level=error' not in content.lower():
    # Check for real errors (not just log level=error)
    lines = content.split('\n')
    errors = [l for l in lines if 'ERROR' in l and 'level=error' not in l.lower()]
    if errors:
        print(f'Build errors found: {errors[-3:]}')
        sys.exit(1)
    print(f'Build in progress ({len(lines)} lines)...')
else:
    print(f'Build in progress ({len(content.split(chr(10)))} lines so far)')

# Swap image in docker-compose
with open(compose_path) as f:
    compose = f.read()

# Find current console image
match = re.search(r'image:\s*(appwrite/console:[^\s\n]+)', compose)
if match:
    old_image = match.group(0)
    new_image = f'image: {image_name}'
    compose_new = compose.replace(old_image, new_image, 1)
    with open(compose_path, 'w') as f:
        f.write(compose_new)
    print(f'Swapped: {old_image} → {new_image}')
elif image_name in compose:
    print(f'Already using {image_name}')
else:
    # Try broader match
    match2 = re.search(r'(image:\s*appwrite/console[^\n]*)', compose)
    if match2:
        old = match2.group(1)
        compose_new = compose.replace(old, f'image: {image_name}', 1)
        with open(compose_path, 'w') as f:
            f.write(compose_new)
        print(f'Swapped: {old} → image: {image_name}')
    else:
        print('Could not find console image line! Searching...')
        for i, line in enumerate(compose.split('\n'), 1):
            if 'console' in line.lower():
                print(f'  {i}: {line}')

print('\nVerify:')
with open(compose_path) as f:
    for i, line in enumerate(f.readlines(), 1):
        if 'console' in line.lower() and 'image' in line.lower():
            print(f'  {i}: {line.strip()}')
