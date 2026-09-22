#!/usr/bin/env python3
"""Import a versioned Moodle connection without changing learner storage settings."""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import sys
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT = re.compile(r'^\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$')


def validate(document):
    if document.get('schema_version') != 1 or document.get('kind') != 'python':
        raise ValueError('Expected Python Lab connection schema version 1')
    platform, tool = document['platform'], document['tool']
    issuer, base = platform['issuer'], tool['base_url']
    for value in (issuer, base):
        parsed = urlsplit(value)
        if parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1') or parsed.path or parsed.query or parsed.fragment or parsed.username:
            raise ValueError('This importer is for HTTP loopback; use the separate production setup for HTTPS')
        if parsed.port == 0:
            raise ValueError('Port must be positive')
    for key, suffix in [('authorize_url','/mod/lti/auth.php'),('jwks_url','/mod/lti/certs.php')]:
        if platform[key] != issuer+suffix:
            raise ValueError('Moodle endpoint mismatch')
    for key, suffix in [('login_url','/hub/lti13/oauth_login'),('callback_url','/hub/lti13/oauth_callback'),('target_url','/hub/user-redirect/lab/')]:
        if tool[key] != base+suffix:
            raise ValueError('Python Lab endpoint mismatch')
    client=platform['client_id']
    if not isinstance(client,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',client) or not str(platform['deployment_id']).isdigit():
        raise ValueError('Invalid registration identifiers')
    return {
        'LAB_AUTH_MODE':'lti13', 'LAB_LOCAL_DEVELOPMENT':'true', 'LAB_PORT':str(urlsplit(base).port or 80),
        'LTI13_ISSUER':issuer, 'LTI13_CLIENT_ID':client, 'LTI13_AUTHORIZE_URL':platform['authorize_url'],
        'LTI13_JWKS_ENDPOINT':'http://moodle-jwks-proxy:8000/jwks', 'LTI13_USERNAME_KEY':'sub',
        'LTI13_URI_SCHEME':'http', 'MOODLE_CANONICAL_HOST':urlsplit(issuer).netloc,
    }


def existing_values(text, keys):
    values={}
    for line in text.splitlines():
        match=ASSIGNMENT.fullmatch(line)
        if not match or match[1] not in keys:
            continue
        if match[1] in values:
            raise ValueError('Duplicate setting: '+match[1])
        tokens=shlex.split(match[2],comments=True)
        if len(tokens)>1 or (tokens and ('$' in tokens[0] or '`' in tokens[0])):
            raise ValueError('Use a literal value for '+match[1])
        values[match[1]]=tokens[0] if tokens else ''
    return values


def merge_env(text, updates):
    remaining=dict(updates); lines=[]
    for line in text.splitlines():
        match=ASSIGNMENT.fullmatch(line)
        if match and match[1] in updates:
            key=match[1]; lines.append(key+'='+updates[key]); remaining.pop(key,None)
        else:
            lines.append(line)
    lines.extend(key+'='+value for key,value in remaining.items())
    return '\n'.join(lines)+'\n'


def atomic_write(path, text):
    with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False,encoding='utf-8') as handle:
        temporary=Path(handle.name)
        handle.write(text)
    try:
        temporary.chmod(0o600)
        os.replace(temporary,path)
    finally:
        temporary.unlink(missing_ok=True)


def connect(path):
    document=json.loads(path.read_text(encoding='utf-8'))
    updates=validate(document)
    target=ROOT/'.env'
    text=target.read_text(encoding='utf-8') if target.exists() else (ROOT/'.env.example').read_text(encoding='utf-8')
    old=existing_values(text,set(updates))
    if target.exists():
        if old.get('LAB_AUTH_MODE','local') != 'lti13':
            raise ValueError('Existing .env is not LTI mode; refusing to reuse local-login identities. Use a separate environment for first LTI setup.')
        for key,value in old.items():
            if key=='LTI13_URI_SCHEME' and value=='auto':
                continue  # Local callback is explicitly HTTP in the imported document.
            if value and 'REPLACE' not in value and value != updates[key]:
                raise ValueError(key+' differs; refusing to rebind existing learner workspaces')
    else:
        # Compose requires this even in LTI mode; it is never enabled as login here.
        updates['LAB_LOCAL_PASSWORD']=secrets.token_urlsafe(32)
        updates['LAB_ADMIN_USERS']=''
    runtime=ROOT/'runtime'; runtime.mkdir(exist_ok=True)
    backup=runtime/'env-before-connect'
    if target.exists() and not backup.exists():
        atomic_write(backup,text)
    atomic_write(target,merge_env(text,updates))
    atomic_write(runtime/'lti-connection.json',json.dumps(document,indent=2)+'\n')
    print('Connection imported. Storage, images, resources and submission settings retained.')
    print('Activity URL: '+document['tool']['target_url'])
    print('Use start-local.sh for basic LTI, or your existing submission-enabled start command.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    link=sub.add_parser('connect'); link.add_argument('connection',type=Path)
    args=parser.parse_args()
    connect(args.connection)


if __name__=='__main__':
    try:
        main()
    except (ValueError,KeyError,TypeError,OSError) as error:
        print('Connection stopped: '+str(error),file=sys.stderr)
        sys.exit(1)
