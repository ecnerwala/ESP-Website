#!/bin/bash
#
# Set up the basic environment on a newly-created server.
#
# Expects:
#  * Fresh Ubuntu install
#  * Logged in as root, directly (not via sudo)
#  * User named 'ubuntu' exists
#  * Shared folder, if any, has *not* been mounted
#

set -euf -o pipefail

# Rename the 'ubuntu' user to 'lu' and give it passwordless sudo. Will fail if
# any processes are currently running under 'ubuntu'.
usermod -l lu ubuntu -d /home/lu -m
groupmod -n lu ubuntu
cat <<EOF > /etc/sudoers.d/90-cloud-init-users
# User rules for lu
lu ALL=(ALL) NOPASSWD:ALL
EOF

# Create and configure the /lu directory. We should do this *before* /lu/share
# is mounted, otherwise the directory will get into a weird state.
mkdir /lu
chown lu:lu /lu
pushd /lu
sudo -u lu git clone https://github.com/learning-unlimited/ESP-Website.git esp-website
popd

# Install chef
export DEBIAN_FRONTEND=noninteractive

apt install -y chef
gem install inifile
