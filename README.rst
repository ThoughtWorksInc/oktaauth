=========================
 oktaauth - Python 3
=========================

The oktaauth module and command line interface allows users to
authenticate with Okta and obtain a SAML assertion either from the
command line or programmatically from another script.

Installation
===========

`python3 setup.py install`

Usage
=====

The oktaauth CLI requires a few arguments to operate.

    # obtain a SAML response from Okta

    $ oktaauth --username joebloggs --server
    acemeinc.okta.com --apptype amazon_aws --appid exk5c0llc

The *apptype* and *appid* are provided by okta and would be seen in the
url when going via a browser.  For example:

    https://acmeinc.okta.com/app/amazon_aws/exk5c0llc/sso/saml

There may be an easier way to obtain this.  If you know then please
submit a pull request to this ``README``.

Thanks
======

Thanks to Okta for help.  I borrowed a lot of code from
https://github.com/okta/okta-openvpn to handle the Okta API
authentication flow.

Authors
=======

* Peter Gillard-Moss
* Matthias Scholz
