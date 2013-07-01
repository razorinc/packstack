
class { 'heat'
  rabbit_host => %(CONFIG_QPID_HOST)s,  # just showing how to use config values in manifests
  
}

class { 'heat::db::mysql':
  password => %(CONFIG_MYSQL_HEAT_PW)s,
}

# You can do whatever you need here
