content = """DATABASE_URL=postgresql://postgres:password@sim-db:5432/postgres

BETTER_AUTH_SECRET=599e2a49b4ea107de6b44953e6f3921b4a78478a449bf58f675b5a543c131e9c
BETTER_AUTH_URL=https://agent.ajstudioz.co.in

NEXT_PUBLIC_APP_URL=https://agent.ajstudioz.co.in

ENCRYPTION_KEY=47e2df67452fc8ac57e07c1fb50dd563bf5cee5a26efe35c396a4c689855fa34
INTERNAL_API_SECRET=1a5a4b864349e12fe0b7f6abf001cc8537d304f755608b0d5d7b50e89570ff65
API_ENCRYPTION_KEY=4d811e5cdbdf7a9c62f4bd048584de6a2145501fa9c04ae3fb34f4e1e4e5d73b

GITHUB_CLIENT_ID=Ov23lisLeFiKw3dDnOk1
GITHUB_CLIENT_SECRET=6487acfc87cfb588584a405b90ef7f6923303ce3

GOOGLE_CLIENT_ID=212163034092-evqog70sit8me1hb1uvipdvag30u2kih.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

RESEND_API_KEY=re_2kV3iMk7_7aPitvGrR4ThmBmRdaT1J3eW

COPILOT_API_KEY=
SIM_AGENT_API_URL=https://agent.ajstudioz.co.in
"""

open('/home/ubuntu/sim/.env', 'w').write(content)
print("ENV updated!")
print("--- Verification ---")
for line in content.strip().split('\n'):
    print(line[:80])
