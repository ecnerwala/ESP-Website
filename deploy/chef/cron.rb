#!/usr/bin/env chef-apply

# Install cron scripts for the website.

template '/etc/conf.d/esp-dbmail' do
  source 'dbmail.cron'
  # TODO: store the randomness somewhere so we don't regenerate the file on
  # every Chef run.
  variables({
    :offset => Random.rand(5),
  })
end
