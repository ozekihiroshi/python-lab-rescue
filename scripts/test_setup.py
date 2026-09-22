import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import setup

DOCUMENT={'schema_version':1,'kind':'python','platform':{
    'issuer':'http://localhost:8083','authorize_url':'http://localhost:8083/mod/lti/auth.php',
    'jwks_url':'http://localhost:8083/mod/lti/certs.php','client_id':'sample-client','deployment_id':'1'},
    'tool':{'base_url':'http://localhost:8086','login_url':'http://localhost:8086/hub/lti13/oauth_login',
    'callback_url':'http://localhost:8086/hub/lti13/oauth_callback','target_url':'http://localhost:8086/hub/user-redirect/lab/'}}
TEMPLATE='LAB_AUTH_MODE=local\nLAB_LOCAL_PASSWORD=CHANGE_ME\nLAB_ADMIN_USERS=admin\nLAB_NETWORK_NAME=python-lab-rescue-internal\nLAB_USER_VOLUME_PREFIX=python-lab-user\n'

class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); patcher=patch.object(setup,'ROOT',self.root)
        patcher.start(); self.addCleanup(patcher.stop)
        (self.root/'.env.example').write_text(TEMPLATE)
        self.document=self.root/'connection.json'; self.document.write_text(json.dumps(DOCUMENT))

    def test_fresh_environment(self):
        setup.connect(self.document)
        values=setup.existing_values((self.root/'.env').read_text(),{'LAB_AUTH_MODE','LAB_LOCAL_PASSWORD','LAB_ADMIN_USERS','LTI13_JWKS_ENDPOINT'})
        self.assertEqual(values['LAB_AUTH_MODE'],'lti13')
        self.assertGreaterEqual(len(values['LAB_LOCAL_PASSWORD']),32)
        self.assertEqual(values['LAB_ADMIN_USERS'],'')
        self.assertEqual(values['LTI13_JWKS_ENDPOINT'],'http://moodle-jwks-proxy:8000/jwks')

    def test_repeat_and_preserve_unrelated_settings(self):
        text="LAB_AUTH_MODE=lti13\nLTI13_CLIENT_ID='sample-client'\nLTI13_URI_SCHEME=auto\nLAB_USER_VOLUME_PREFIX=existing-user\nPYTHON_LAB_SUBMIT_SECRET='test-only-value'\nLAB_SINGLEUSER_IMAGE=existing:version\n"
        target=self.root/'.env'; target.write_text(text)
        setup.connect(self.document); before=target.read_bytes(); setup.connect(self.document)
        self.assertEqual(before,target.read_bytes())
        self.assertEqual((self.root/'runtime/env-before-connect').read_text(),text)
        for line in text.splitlines()[3:]: self.assertIn(line,target.read_text())

    def test_rebinding_refused_before_writes(self):
        target=self.root/'.env'; target.write_text('LAB_AUTH_MODE=lti13\nLTI13_CLIENT_ID=someone-else\n')
        before=target.read_bytes()
        with self.assertRaises(ValueError): setup.connect(self.document)
        self.assertEqual(before,target.read_bytes()); self.assertFalse((self.root/'runtime').exists())

    def test_existing_local_mode_refused(self):
        (self.root/'.env').write_text(TEMPLATE)
        with self.assertRaisesRegex(ValueError,'not LTI mode'): setup.connect(self.document)

    def test_wrong_kind_endpoint_and_payload_refused(self):
        variants=[]
        for key,value in [('kind','java'),('schema_version',2)]: variants.append(dict(DOCUMENT,**{key:value}))
        for key,value in [('client_id','bad\nENV=x'),('jwks_url','http://elsewhere/keys')]:
            d=copy.deepcopy(DOCUMENT); d['platform'][key]=value; variants.append(d)
        d=copy.deepcopy(DOCUMENT); d['tool']['target_url']='http://localhost:8086/hub/user-redirect/ide/'; variants.append(d)
        for d in variants:
            with self.assertRaises(ValueError): setup.validate(d)
        self.assertFalse((self.root/'.env').exists())

    def test_duplicates_refused_and_crlf_supported(self):
        with self.assertRaises(ValueError): setup.existing_values('LAB_PORT=8086\nLAB_PORT=99',{'LAB_PORT'})
        self.assertEqual(setup.existing_values('export LAB_PORT="8086"\r\n',{'LAB_PORT'}),{'LAB_PORT':'8086'})

if __name__=='__main__': unittest.main()
