# Installs & configure the heat engine service

class heat::engine (
  $enabled           = true,
  $keystone_host     = '127.0.0.1',
  $keystone_port     = '35357',
  $keystone_protocol = 'http',
  $keystone_user     = 'heat',
  $keystone_tenant   = 'services',
  $keystone_password = 'password',
  $bind_host         = '0.0.0.0',
  $bind_port         = '8001',
  $verbose           = 'False',
  $debug             = 'False',
  $heat_stack_user_role          = 'heat_stack_user',
  $heat_metadata_server_url      = 'http://127.0.0.1:8000',
  $heat_waitcondition_server_url = 'http://127.0.0.1:8000/v1/waitcondition',
  $heat_watch_server_url         = 'http://127.0.0.1:8003',
) {

  include heat::params

  validate_string($keystone_password)

  Heat_engine_config<||> ~> Service['heat-engine']

  Package['heat-engine'] -> Heat_engine_config<||>
  Package['heat-engine'] -> Service['heat-engine']
  package { 'heat-engine':
    ensure => installed,
    name   => $::heat::params::engine_package_name,
  }

  file { '/etc/heat/heat-engine.conf':
    owner   => 'heat',
    group   => 'heat',
    mode    => '0640',
  }

  if $enabled {
    $service_ensure = 'running'
  } else {
    $service_ensure = 'stopped'
  }

  Package['heat-common'] -> Service['heat-engine']

  if $rabbit_hosts {
    heat_engine_config { 'DEFAULT/rabbit_host': ensure => absent }
    heat_engine_config { 'DEFAULT/rabbit_port': ensure => absent }
    heat_engine_config { 'DEFAULT/rabbit_hosts':
      value => join($rabbit_hosts, ',')
    }
  } else {
    heat_engine_config { 'DEFAULT/rabbit_host': value => $rabbit_host }
    heat_engine_config { 'DEFAULT/rabbit_port': value => $rabbit_port }
    heat_engine_config { 'DEFAULT/rabbit_hosts':
      value => "${rabbit_host}:${rabbit_port}"
    }
  }

  if size($rabbit_hosts) > 1 {
    heat_engine_config { 'DEFAULT/rabbit_ha_queues': value => true }
  } else {
    heat_engine_config { 'DEFAULT/rabbit_ha_queues': value => false }
  }

  service { 'heat-engine':
    ensure     => $service_ensure,
    name       => $::heat::params::engine_service_name,
    enable     => $enabled,
    hasstatus  => true,
    hasrestart => true,
    require    => Class['heat::db'],
  }

  heat_engine_config {
    'DEFAULT/rabbit_userid'          : value => $rabbit_userid;
    'DEFAULT/rabbit_password'        : value => $rabbit_password;
    'DEFAULT/rabbit_virtualhost'     : value => $rabbit_virtualhost;
    'DEFAULT/debug'                  : value => $debug;
    'DEFAULT/verbose'                : value => $verbose;
    'DEFAULT/log_dir'                : value => $::heat::params::log_dir;
    'DEFAULT/bind_host'              : value => $bind_host;
    'DEFAULT/bind_port'              : value => $bind_port;
    'DEFAULT/heat_stack_user_role'         : value => $heat_stack_user_role;
    'DEFAULT/heat_metadata_server_url'     : value => $heat_metadata_server_url;
    'DEFAULT/heat_waitcondition_server_url': value => $heat_waitcondition_server_url;
    'DEFAULT/heat_watch_server_url'        : value => $heat_watch_server_url;
  }
}
