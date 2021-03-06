# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys

from heatclient import client as heat_client

if os.environ.has_key('OS_AUTH_URL'):
  if os.environ['OS_AUTH_URL'].endswith('/v3'):
      from keystoneclient.v3 import client as ksclient
  else:
      from keystoneclient.v2_0 import client as ksclient

import logging
global LOG
LOG = logging.getLogger('cloudutils')

def get_ksclient(**kwargs):
    """Get an endpoint and auth token from Keystone.

    :param username: name of user
    :param password: user's password
    :param tenant_id: unique identifier of tenant
    :param tenant_name: name of tenant
    :param auth_url: endpoint to authenticate against
    :param token: token to use instead of username/password
    """
    kc_args = {'auth_url': kwargs.get('auth_url'),
               'insecure': kwargs.get('insecure'),
               'cacert': kwargs.get('cacert')}

    if kwargs.get('tenant_id'):
        kc_args['tenant_id'] = kwargs.get('tenant_id')
    else:
        kc_args['tenant_name'] = kwargs.get('tenant_name')

    if kwargs.get('token'):
        kc_args['token'] = kwargs.get('token')
    else:
        kc_args['username'] = kwargs.get('username')
        kc_args['password'] = kwargs.get('password')

    return ksclient.Client(**kc_args)


# Magic function: gets keystone endpoints from environment without requiring admin privileges

def get_endpoint(client, **kwargs):
    """Get an endpoint using the provided keystone client."""
    if kwargs.get('region_name'):
        return client.service_catalog.url_for(
            service_type=kwargs.get('service_type') or 'orchestration',
            attr='region',
            filter_value=kwargs.get('region_name'),
            endpoint_type=kwargs.get('endpoint_type') or 'publicURL')
    return client.service_catalog.url_for(
        service_type=kwargs.get('service_type') or 'orchestration',
        endpoint_type=kwargs.get('endpoint_type') or 'publicURL')

# Get Keystone credentials from environment

missing_keys = False

keystone_kwargs = {}

for key in ['username', 'password', 'auth_url', 'tenant_name']:
  if os.environ.has_key('OS_' + key.upper()):
    keystone_kwargs[key] = os.environ['OS_' + key.upper()]
  else:
    missing_keys = True
    print('Required Environment variable OS_%s unset.' % key.upper(), file=sys.stderr)

if missing_keys:
  print('Missing environment variables, exiting.', file=sys.stderr)
  exit(1)

if os.environ['OS_AUTH_URL'].endswith('/v3'):

  # First, catch missing 'default'... 
  # (Can happen due to openrc generated by a cloud without the fix for
  # https://bugs.launchpad.net/horizon/+bug/1460150)
  for var in [ 'user_domain_id', 'project_name', 'project_domain_id' ]:
    if os.environ.has_key('OS_' + var.upper()):
      keystone_kwargs[var] = os.environ['OS_' + var.upper()]
    else:
      keystone_kwargs[var] = 'default'

  # ...then ensure Keys That Must Remain Unset are (it's either these or
  # the ones above, not both).
  for var in [ 'user_id', 'user_domain_name', 'project_domain_name' ]:
    if os.environ.has_key('OS_' + var.upper()):
      keystone_kwargs[var] = os.environ['OS_' + var.upper()]
    else:
      keystone_kwargs[var] = None

# Authenticate with keystone

# Heat

#ksclient = get_ksclient(**keystone_kwargs)
#endpoint = get_endpoint(ksclient, **keystone_kwargs)

#client = heat_client.Client('1', endpoint, token=ksclient.auth_ref['token']['id'], **keystone_kwargs)

#fields = {'stack_id': argv[1]}
#stack = client.stacks.get(**fields)

#print "%s - %s" % (stack.stack_status, stack.stack_status_reason)

