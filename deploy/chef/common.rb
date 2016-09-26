# This file is included in every Chef script.

require 'inifile'

if Etc.getpwuid.uid != 0
  abort 'ERROR: this script must be run as root'
end

REPO = File.expand_path("../../../", __FILE__)
TEMPLATES = File.join(REPO, "deploy", "config_templates")

['/lu/share/chapter.ini', '~/chapter.ini'].each do |filename|
  INI = IniFile.load(File.expand_path(filename))
  break unless INI.nil?
end

if INI.nil?
  abort 'ERROR: chapter.ini not found'
end
CONFIG = INI['config']
DISPLAY = INI['display']
SECRET = INI['secret']

def http_hostname
  CONFIG.fetch('domain-override') || "#{CONFIG.fetch('slug')}.learningu.org"
end
