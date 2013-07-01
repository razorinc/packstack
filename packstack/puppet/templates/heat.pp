#  rabbit_host => "%(CONFIG_QPID_HOST)s",
class { 'heat':
  qpid_hostname => "%(CONFIG_QPID_HOST)s",
  keystone_auth_host => "%(CONFIG_KEYSTONE_HOST)s",
  rpc_backend => 'heat.openstack.common.rpc.impl_qpid',
  bind_host => '%(CONFIG_HEAT_HOST)s',
  verbose     => true,
  debug       => true,
}

class {'heat::api-cfn':
  bind_host => '%(CONFIG_HEAT_API_CFN_HOST)s',
  auth_uri=>'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
  keystone_host => '%(CONFIG_KEYSTONE_HOST)s',
  verbose => true,
  debug => true,
  keystone_password => "%(CONFIG_HEAT_KS_PW)s",
}

class {'heat::api-cloudwatch':
  bind_host => '%(CONFIG_HEAT_API_CLOUDWATCH_HOST)s',
  auth_uri=>'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
  keystone_host => '%(CONFIG_KEYSTONE_HOST)s',
  verbose => true,
  debug => true,
  keystone_password => "%(CONFIG_HEAT_KS_PW)s",
}

class { 'heat::api':
  keystone_password => "%(CONFIG_HEAT_KS_PW)s",
  verbose => true,
  debug => true,
  bind_host => '%(CONFIG_HEAT_API_HOST)s',
}

# Install heat-engine
class { 'heat::engine':
  verbose => true,
  debug => true,
  keystone_password => "%(CONFIG_HEAT_KS_PW)s",
  heat_metadata_server_url => "%(CONFIG_HEAT_ENGINE_HOST)s",
  bind_host => '%(CONFIG_HEAT_API_HOST)s',
}
