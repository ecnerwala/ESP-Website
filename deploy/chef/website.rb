#!/usr/bin/env chef-apply

# Install the dependencies required to run the website (Python, etc.). Web
# servers and databases are managed separately.

package 'python'
package 'python-setuptools'
package 'python-pip'

execute 'pip install --upgrade -r requirements.txt' do
  cwd '/lu/esp-website/esp'
  # Note: this command will get run a lot, so make sure to pin the versions of
  # all dependencies.
end
