#!/usr/bin/env chef-apply

# Installs uWSGI and configures it to serve the website.

package 'uwsgi'
package 'uwsgi-plugin-python'

service 'uwsgi' do
  supports :status => true, :restart => true, :reload => true
end

template '/etc/uwsgi/apps-available/esp.ini' do
  source 'esp.ini'
  owner 'root'
  group 'root'
  mode '0644'
  notifies :reload, 'service[uwsgi]', :immediately
end

link '/etc/uwsgi/apps-enabled/esp.ini' do
  to '../apps-available/esp.ini'
  notifies :reload, 'service[uwsgi]', :immediately
end

file '/var/log/uwsgi/app/esp.ini' do
  # By default the logfie is only readable by root. To change this, we create
  # the file now and set its group.
  group 'adm'
end
