#  rabbit_host => "%(CONFIG_QPID_HOST)s",
class { 'heat':

}

# Install heat-engine

class { 'heat::api':
  keystone_password => "%(CONFIG_HEAT_KS_PW)s",
}

class { 'heat::engine':
}

# You can do whatever you need here
