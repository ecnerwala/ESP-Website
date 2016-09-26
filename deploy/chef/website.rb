#!/usr/bin/env chef-apply
#
# Install the dependencies required to run the website (Python, etc.). Web
# servers and databases are managed separately.

require_relative 'common'

package 'python'
package 'python-setuptools'
package 'python-pip'

# Python packages that have compiled binary dependencies will be installed with
# apt, not pip.
package 'python-psycopg2'
package 'python-pycurl'
package 'python-pylibmc'

execute 'pip install --upgrade --no-cache-dir -r requirements.txt' do
  cwd "#{REPO}/esp"
  # Note: this command will get run a lot, so make sure to pin the versions of
  # all dependencies.
end

tempalte "#{REPO}/esp/esp/local_settings.py" do
  source "#{TEMPLATES}/local_settings.chef.py"
  local true
end
