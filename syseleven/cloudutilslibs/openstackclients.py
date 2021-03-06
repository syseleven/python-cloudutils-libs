# -*- coding: utf-8 -*-

import os
from copy import deepcopy

# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
try:
    import requests
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass

### python openstack clients ###
# heat
from heatclient import client as heat_client

# neutron
from neutronclient.neutron import client as neutron_client

# nova
from keystoneclient.auth.identity import v2
from keystoneclient.auth.identity import v3
from keystoneclient import session
from novaclient.client import Client as nova_client

from syseleven.cloudutilslibs.kclient import (keystone_kwargs,
                                        get_ksclient,
                                        get_endpoint)

from syseleven.cloudutilslibs.utils import dict_merge

import logging
global LOG
LOG = logging.getLogger('cloudutils')

def get_heat_client(keystone_env = {}):
    _keystone_kwargs = deepcopy(keystone_kwargs)
    ksclient = get_ksclient(**_keystone_kwargs)
    _keystone_kwargs['service_type'] = 'orchestration'
    _keystone_kwargs = dict_merge(_keystone_kwargs, keystone_env)
    LOG.debug('keystone auth: %s' % _keystone_kwargs)
    endpoint = get_endpoint(ksclient, **_keystone_kwargs)
    if os.environ['OS_AUTH_URL'].endswith('/v3'):
        token = ksclient.auth_ref['auth_token']
    else:
        token = ksclient.auth_ref['token']['id']
    client = heat_client.Client('1', endpoint=endpoint, token=token, **_keystone_kwargs)

    return client

def get_neutron_client(keystone_env = {}):
    _keystone_kwargs = deepcopy(keystone_kwargs)
    ksclient = get_ksclient(**_keystone_kwargs)
    _keystone_kwargs['service_type'] = 'network'
    _keystone_kwargs = dict_merge(_keystone_kwargs, keystone_env)
    LOG.debug('keystone auth: %s' % _keystone_kwargs)
    endpoint = get_endpoint(ksclient, **_keystone_kwargs)
    if os.environ['OS_AUTH_URL'].endswith('/v3'):
        token = ksclient.auth_ref['auth_token']
    else:
        token = ksclient.auth_ref['token']['id']
    client = neutron_client.Client('2.0', endpoint_url=endpoint, token=token, **_keystone_kwargs)

    return client

def get_nova_client(keystone_env = {}):
    _keystone_kwargs = deepcopy(keystone_kwargs)
    if 'service_type' in _keystone_kwargs:
        del _keystone_kwargs['service_type']
    _keystone_kwargs = dict_merge(_keystone_kwargs, keystone_env)
    LOG.debug('keystone auth: %s' % _keystone_kwargs)
    if os.environ['OS_AUTH_URL'].endswith('/v3'):
        if _keystone_kwargs.has_key('tenant_name'):
          del _keystone_kwargs['tenant_name']
        nova_auth = v3.Password(**_keystone_kwargs)
    else:
        nova_auth = v2.Password(**_keystone_kwargs)

    nova_session = session.Session(auth=nova_auth)
    client = nova_client('2', session=nova_session)

    return client


