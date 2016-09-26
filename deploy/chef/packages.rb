#!/usr/bin/env chef-apply

# Installs base Ubuntu packages. For now, pulls this list from
# packages_base.txt.

packages = File.readlines(
  File.join(File.dirname(__FILE__), "../../esp/packages_base.txt")
)

packages.each do |p|
  package p
end
