#!/usr/bin/env chef-apply
#
# Installs base Ubuntu packages and configuration.

require_relative 'common'

# Set hostname.
file '/etc/hostname' do
  content unix_shortname
end

template '/etc/hosts' do
  source "#{TEMPLATES}/hosts"
  local true
  variables({
    :fqdn => unix_fqdn,
    :hostname => unix_hostname,
  })
end

# Install packages. For now, pulls this list from packages_base.txt.
packages = File.readlines(
  File.join(File.dirname(__FILE__), "../../esp/packages_base.txt")
)

packages.each do |p|
  package p
end

# Helpful packges
package 'htop'
package 'emacs'
