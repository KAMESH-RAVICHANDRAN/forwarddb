#!/usr/bin/env python3
path = '/etc/nginx/sites-available/agent.ajstudioz.co.in'
with open(path) as f:
    content = f.read()

socket_block = """
    # Realtime WebSocket (socket.io on port 3002)
    location /socket.io/ {
        proxy_pass http://localhost:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }
"""

if 'socket.io' in content:
    print('Already has socket.io block, skipping')
else:
    content = content.replace('    listen 443 ssl;', socket_block + '    listen 443 ssl;', 1)
    with open(path, 'w') as f:
        f.write(content)
    print('Patched successfully!')

# Show result
with open(path) as f:
    lines = f.readlines()
print(f'\nNginx config ({len(lines)} lines):')
for i, l in enumerate(lines, 1):
    print(f'{i:3}: {l}', end='')
