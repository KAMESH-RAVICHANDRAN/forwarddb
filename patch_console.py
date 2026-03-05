import re

# Patch login page
path = '/home/ubuntu/console/src/routes/(public)/(guest)/login/+page.svelte'

with open(path, 'r') as f:
    content = f.read()

# 1. Fix page title
content = content.replace('<title>Sign in - Appwrite</title>', '<title>Sign in - ForwardDB BY AJ STUDIOZ</title>')

# 2. Add onGoogleLogin function before closing </script>
google_fn = """
    function onGoogleLogin() {
        let url = window.location.origin;
        if (page.url.searchParams) {
            const redirect = page.url.searchParams.get('redirect');
            page.url.searchParams.delete('redirect');
            if (redirect) {
                url = redirect + page.url.search;
            } else {
                url = base + (page.url.search ?? '');
            }
        }
        sdk.forConsole.account.createOAuth2Session({
            provider: OAuthProvider.Google,
            success: window.location.origin + url,
            failure: window.location.origin
        });
    }
"""
content = content.replace('</script>', google_fn + '</script>', 1)

# 3. Remove {#if isCloud} block but keep its inner content
content = re.sub(r'\s*\{#if isCloud\}', '', content)
content = re.sub(r'\s*\{/if\}', '', content)

# 4. Add Google button after the GitHub button (find the "Sign in with GitHub" button closing tag)
content = content.replace(
    '                        <span class="text">Sign in with GitHub</span>\n                    </Button>',
    '                        <span class="text">Sign in with GitHub</span>\n                    </Button>\n                <Button secondary fullWidth on:click={onGoogleLogin} {disabled}>\n                    <span class="text">Sign in with Google</span>\n                </Button>'
)

with open(path, 'w') as f:
    f.write(content)
print('Login page patched!')

# Patch footer branding
import os
footer_path = '/home/ubuntu/console/src/lib/layout/footer.svelte'
if os.path.exists(footer_path):
    with open(footer_path, 'r') as f:
        fc = f.read()
    fc = re.sub(r'© \d+ Appwrite', '© 2026 ForwardDB BY AJ STUDIOZ', fc)
    fc = fc.replace('>Appwrite<', '>ForwardDB BY AJ STUDIOZ<')
    with open(footer_path, 'w') as f:
        f.write(fc)
    print('Footer patched!')

# Patch unauthenticated layout logo alt text
layout_path = '/home/ubuntu/console/src/lib/layout/unauthenticated.svelte'
if os.path.exists(layout_path):
    with open(layout_path, 'r') as f:
        lc = f.read()
    lc = lc.replace('alt="Appwrite Logo"', 'alt="ForwardDB Logo"')
    lc = lc.replace('alt="Appwrite"', 'alt="ForwardDB BY AJ STUDIOZ"')
    with open(layout_path, 'w') as f:
        f.write(lc)
    print('Layout patched!')

# Verify
print('\n--- Login page verification ---')
with open(path, 'r') as f:
    for i, line in enumerate(f, 1):
        if any(x in line for x in ['title', 'Google', 'isCloud', 'GitHub', 'github']):
            print(f'{i}: {line.rstrip()}')
