#!/bin/bash
#
# Jakob Janzen
# jakob.janzen80@gmail.com
# 2025-10-31
#
# Ubuntu setup script.
#
export CWD="$PWD"

usage()
{
  echo "Usage: $(basename "$0") [OPTIONS]
  -m, --linux-mint-ubuntu   Linux-Mint Ubuntu setup.
  -u, --ubuntu              Ubuntu setup.
  -h, --help                Show this help and quit.
  "
  exit 1
}

TEMP=$(getopt -o 'muh' --long 'linux-mint-ubuntu,ubuntu,help' -- "$@")
# shellcheck disable=SC2181
if [[ $? -ne 0 ]]
then
  usage
fi
eval set -- "$TEMP"
unset TEMP
SETUP=
while true
do
  case "$1" in
  '-m' | '--linux-mint-ubuntu')
    echo ""
    SETUP=linuxmintubuntu
    shift
    continue
    ;;
  '-u' | '--ubuntu')
    SETUP=ubuntu
    shift
    continue
    ;;
  '-h' | '--help')
    usage
    ;;
  '--')
    shift
    break
    ;;
  esac
done
[[ -n $SETUP ]] || usage

function initial_update
{
  sudo apt update && sudo apt upgrade -y
  sudo apt full-upgrade -y
  sudo apt install -y nala
}

function nala_install
{
  # shellcheck disable=SC2068
  for item in $@
  do
    (
      dpkg --get-selections "$item" | grep --word-regexp "install"
    ) || sudo nala install -y "$item"
  done
}

function nala_remove
{
  # shellcheck disable=SC2068
  for item in $@
  do
    (
      dpkg --get-selections "$item" | grep --word-regexp "install"
    ) && sudo nala purge -y "$item" || echo "$item not installed"
  done
}

function sysctl_add
{
  grep "$1" /etc/sysctl.conf >/dev/null 2>&1 && sudo sed -i '/'"$1"'/d' /etc/sysctl.conf
  sudo bash -c "echo \"$1 = $2\" >> /etc/sysctl.conf"
}

echo "
update packages:"
initial_update

PKG_LINUXMINTUBUNTU="
"

PKG_UBUNTU="
  gnome-tweaks
"

PKG_SYSTEM="
  ubuntu-restricted-extras
  unattended-upgrades
  ubuntu-standard
  aptitude
  apt-transport-https
"
PKG_GENERAL="
  preload
  file-roller
  cheese
  meld
  transmission
  hunspell
  hunspell-de-de
  hunspell-en-us
  aspell
  aspell-de
  aspell-en
  gcolor3
"
PKG_CLI="
  hwinfo
  neovim
  openssh-server
  wget
  gpg
  tree
  duf
  btop
  neofetch
  htop
  iotop
  nmon
  net-tools
"
PKG_OFFICE="
  libreoffice
  libreoffice-l10n-de
  libreoffice-help-de
  libreoffice-style-sifr
"
PKG_GRAPHICS="
  gimp
  gimp-help-de
  inkscape
"
PKG_MULTIMEDIA="
  vlc
  vlc-l10n
  vlc-plugin-visualization
  mpv
"
PKG_CODECS="
  faac
  libfdk-aac2
  fdkaac
  aften
  lame
  speex
  libavif-bin
  dav1d
  rav1e
  svt-av1
  davs2
  x264
  x265
  mkvtoolnix
  ogmtools
  ffmpeg
"
PKG_COMPRESSION="
  bzip2
  lbzip2
  pbzip2
  bzip3
  gzip
  pigz
  lrzip
  lz4
  lzip
  plzip
  lzop
  pixz
  zstd
  7zip
  dar
  tar
  rar
  unrar
  tarlz
  zip
  unzip
  unar
  zpaq
  lhasa
  unace
  cabextract
"
PKG_DEVELOPMENT="
  build-essential
  python-is-python3
  python3-pip
  python3-autopep8
  python3-poetry
  python3-pytest
  python3-flake8
  pipenv
  black
  make
  cmake
  clang
  clang-tidy
  clang-format
  clang-tools
  curl
  ca-certificates
  libssl-dev
  libmagic-dev
  libmagickwand-dev
  git
  default-jdk
  shellcheck
  shfmt
  valgrind
  zeal
"

PKG_REMOVE="
  thunderbird
  vim
  vim-common
  vim-tiny
"

echo "
install packages:"
case "$SETUP" in
linuxmintubuntu)
  if [[ -n $PKG_LINUXMINTUBUNTU ]]
  then
    echo "Linux-Mint Ubuntu"
    nala_install $PKG_LINUXMINTUBUNTU
  fi
  ;;
ubuntu)
  if [[ -n $PKG_UBUNTU ]]
  then
    echo "Ubuntu"
    nala_install $PKG_UBUNTU
  fi
  ;;
esac
# shellcheck disable=SC2086
nala_install \
  $PKG_SYSTEM \
  $PKG_GENERAL \
  $PKG_CLI \
  $PKG_OFFICE \
  $PKG_GRAPHICS \
  $PKG_MULTIMEDIA \
  $PKG_CODECS \
  $PKG_COMPRESSION \
  $PKG_DEVELOPMENT

# VS CODE
echo "
install VS Code:"
if dpkg --get-selections "code" | grep --word-regexp "install"
then
  echo "VS Code installed"
else
  cd /tmp && pwd || echo
  wget -qO- https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor >packages.microsoft.gpg
  sudo install -D -o root -g root -m 644 packages.microsoft.gpg \
    /etc/apt/keyrings/packages.microsoft.gpg
  sudo rm -v /etc/apt/sources.list.d/vscode.*
  echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] " \
    "https://packages.microsoft.com/repos/code stable main" | \
    sudo tee /etc/apt/sources.list.d/vscode.list >/dev/null
  rm -fv packages.microsoft.gpg
  sudo nala update
  sudo nala install -y code
  cd "$CWD" && pwd || echo
fi

# REMOVE
echo "
remove packages:"
# shellcheck disable=SC2086
nala_remove \
  $PKG_REMOVE
sudo update-alternatives --remove vim /usr/bin/vim

# CLEAN
echo "
autopurge packages:"
sudo nala autopurge -y

# SNAP
case $SETUP in
linuxmintubuntu)
  if [[ -n $PKG_LINUXMINTUBUNTU ]]
  then
    echo "
    manage flatpak:"
    echo "Linux-Mint Ubuntu"
    flatpak list
    flatpak update
  fi
  ;;
ubuntu)
  if [[ -n $PKG_UBUNTU ]]
  then
    echo "
    manage snap:"
    echo "Ubuntu"
    sudo snap refresh
  fi
  ;;
esac

# ENVIRONMENT
echo "
updating /etc/environment:"
grep "JAVA_HOME=" /etc/environment >/dev/null 2>&1 && sudo sed -i '/JAVA_HOME=/d' /etc/environment
sudo bash -c 'echo "JAVA_HOME=$(update-alternatives --list java)" >> /etc/environment'
cat /etc/environment
echo

# SYSTCTL
sudo sed -i '/^[a-z]/d' /etc/sysctl.conf

sysctl_add "kernel.printk" "3 4 1 3"
sysctl_add "kernel.sysrq" 0

sysctl_add "vm.dirty_background_ratio" 2
sysctl_add "vm.dirty_ratio" 60
sysctl_add "vm.swappiness" 10

sysctl_add "net.ipv4.conf.all.accept_redirects" 0
sysctl_add "net.ipv4.conf.all.accept_source_route" 0
sysctl_add "net.ipv4.conf.all.log_martians" 1
sysctl_add "net.ipv4.conf.all.rp_filter" 1
sysctl_add "net.ipv4.conf.all.secure_redirects" 0
sysctl_add "net.ipv4.conf.all.send_redirects" 0

sysctl_add "net.ipv4.conf.default.accept_redirects" 0
sysctl_add "net.ipv4.conf.default.accept_source_route" 0
sysctl_add "net.ipv4.conf.default.rp_filter" 1
sysctl_add "net.ipv4.conf.default.secure_redirects" 0
sysctl_add "net.ipv4.conf.default.send_redirects" 0

sysctl_add "net.ipv4.icmp_echo_ignore_all" 1
sysctl_add "net.ipv4.icmp_echo_ignore_broadcasts" 1
sysctl_add "net.ipv4.ip_forward" 0

sysctl_add "net.ipv4.tcp_max_syn_backlog" 5120
sysctl_add "net.ipv4.tcp_syn_retries" 3
sysctl_add "net.ipv4.tcp_synack_retries" 5
sysctl_add "net.ipv4.tcp_syncookies" 1

sysctl_add "net.ipv6.conf.default.accept_ra_defrtr" 0
sysctl_add "net.ipv6.conf.default.accept_ra_pinfo" 0
sysctl_add "net.ipv6.conf.default.accept_ra_rtr_pref" 0
sysctl_add "net.ipv6.conf.default.autoconf" 0
sysctl_add "net.ipv6.conf.default.dad_transmits" 0
sysctl_add "net.ipv6.conf.default.max_addresses" 1
sysctl_add "net.ipv6.conf.default.router_solicitations" 0

sudo sysctl --system

# SERVICES
sudo systemctl enable --now ssh
sudo systemctl --no-pager status ssh

sudo systemctl enable --now preload
sudo systemctl --no-pager status preload

sudo systemctl restart systemd-sysctl
sudo systemctl --no-pager status systemd-sysctl
