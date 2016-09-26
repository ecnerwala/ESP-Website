#!/usr/bin/env chef-apply

# Installs and configures memcached.

package 'memcached'

service 'memcached' do
  supports :status => true, :restart => true
end

template '/etc/memcached.conf' do
  source 'memcached.conf'
  notifies :restart, 'service[memcached]', :immediately
end
