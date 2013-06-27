
class { 'heat'
  rabbit_host => %(CONFIG_QPID_HOST)s,  # just showing how to use config values in manifests
}

# You can do whatever you need here
