import requests
import base64
from urllib.parse import urlparse
import logging
from bs4 import BeautifulSoup
log = logging.getLogger('oktaauthpy3')

class OktaAPIAuth(object):

    def __init__(self, okta_server, username, password, passcode):
        passcode_len = 6
        self.okta_url = None
        self.username = username
        self.password = password
        self.passcode = passcode
        url_new = ('https', okta_server,
                   '', '', '','')
        self.okta_url = urlparse.urlunparse(url_new)
        return

    def okta_req(self, path, data):
        url = '{base}/api/v1{path}'.format(base=self.okta_url, path=path)
        resp = requests.post(url=url, headers={'Accept': 'application/json',
                                               'Content-Type': 'application/json'}, json=data)
        return resp.json()

    def preauth(self):
        path = '/authn'
        data = {'username': self.username,
                'password': self.password}
        return self.okta_req(path, data)

    def doauth(self, fid, state_token):
        path = '/authn/factors/{fid}/verify'.format(fid=fid)
        data = {'fid': fid,
                'stateToken': state_token,
                'passCode': self.passcode}
        return self.okta_req(path, data)

    def auth(self):
        username = self.username
        password = self.password
        status = False
        rv = False
        invalid_username_or_password = username is None or username == '' or password is None or password == ''
        if invalid_username_or_password:
            log.info("Missing username or password for user: {} ({}) - Reported username may be 'None' due to this".format(username))
            return False
        else:
            if not self.passcode:
                log.info('No second factor found for username %s' % username)
            log.debug('Authenticating username %s' % username)
            try:
                rv = self.preauth()
            except Exception as s:
                log.error('Error connecting to the Okta API: %s' % s)
                return False

            if 'errorCauses' in rv:
                msg = rv['errorSummary']
                log.info('User %s pre-authentication failed: %s' % (self.username, msg))
                return False
            if 'status' in rv:
                status = rv['status']
            if status == 'SUCCESS':
                log.info('User %s authenticated without MFA' % self.username)
                return rv['sessionToken']
            if status == 'MFA_ENROLL' or status == 'MFA_ENROLL_ACTIVATE':
                log.info('User %s needs to enroll first' % self.username)
                return False
            if status == 'MFA_REQUIRED' or status == 'MFA_CHALLENGE':
                log.debug('User %s password validates, checking second factor' % self.username)
                res = None
                for factor in rv['_embedded']['factors']:
                    if factor['factorType'] != 'token:software:totp':
                        continue
                    fid = factor['id']
                    state_token = rv['stateToken']
                    try:
                        res = self.doauth(fid, state_token)
                    except Exception as s:
                        log.error('Unexpected error with the Okta API: %s' % s)
                        return False

                    if 'status' in res and res['status'] == 'SUCCESS':
                        log.info('User %s is now authenticated with MFA via Okta API' % self.username)
                        return res['sessionToken']

                if 'errorCauses' in res:
                    msg = res['errorCauses'][0]['errorSummary']
                    log.debug('User %s MFA token authentication failed: %s' % (self.username, msg))
                return False
            log.info('User %s is not allowed to authenticate: %s' % (self.username, status))
            return False
            return


class OktaSamlAuth(OktaAPIAuth):

    def __init__(self, okta_url, application_type, application_id, username, password, passcode):
        self.application_type = application_type
        self.application_id = application_id
        OktaAPIAuth.__init__(self, okta_url, username, password, passcode)

    def saml(self, sessionToken):
        url = '{base}/app/{app}/{appid}/sso/saml'.format(base=self.okta_url, app=self.application_type, appid=self.application_id)
        resp = requests.get(url=url, params={'onetimetoken': sessionToken})

        if resp.status_code != 200:
            raise Exception('Received error code from server: %s' % resp.status_code)

        return resp.text.decode('utf8')

    def assertion(self, saml):
        assertion = ''
        soup = BeautifulSoup(saml, 'html.parser')
        for inputtag in soup.find_all('input'):
            if inputtag.get('name') == 'SAMLResponse':
                assertion = inputtag.get('value')

        return base64.b64decode(assertion)

    def auth(self):
        token = super(OktaSamlAuth, self).auth()
        if not token:
            return False
        return self.assertion(self.saml(token))
