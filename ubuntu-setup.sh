#!/bin/bash
#
# Jakob Janzen
# jakob.janzen80@gmail.com
# 2025-07-20
#
export CWD="$PWD"

function initial_update
{
  sudo apt update && sudo apt upgrade -y
  sudo apt full-upgrade -y
  sudo apt install -y nala
}

function nala_install
{
  for item in $@
  do
    (
      dpkg --get-selections "$item" | grep --word-regexp "install"
    ) || sudo nala install -y "$item"
  done
}

function nala_remove
{
  for item in $@
  do
    (
      dpkg --get-selections "$item" | grep --word-regexp "install"
    ) && sudo nala purge -y "$item" || echo "$item not installed"
  done
}

initial_update

# SYSTEM
nala_install \
  ubuntu-restricted-extras \
  unattended-upgrades \
  ubuntu-standard \
  aptitude \
  apt-transport-https

# GENERAL
nala_install \
  preload \
  gnome-tweaks \
  file-roller \
  cheese

# CLI
nala_install \
  hwinfo \
  neovim \
  openssh-server \
  wget \
  gpg \
  tree \
  duf \
  btop \
  neofetch \
  htop \
  iotop \
  nmon \
  net-tools

# OFFICE
nala_install \
  libreoffice \
  libreoffice-l10n-de \
  libreoffice-help-de \
  libreoffice-style-sifr

# GRAPHICS
nala_install \
  gimp \
  gimp-help-de \
  inkscape

# MULTIMEDIA
nala_install \
  vlc \
  vlc-l10n \
  vlc-plugin-visualization

# CODECS
nala_install \
  faac \
  libfdk-aac2 \
  fdkaac \
  aften \
  lame \
  speex \
  libavif-bin \
  dav1d \
  rav1e \
  svt-av1 \
  davs2 \
  x264 \
  x265 \
  mkvtoolnix \
  ogmtools \
  ffmpeg

# COMPRESSION
nala_install \
  bzip2 \
  lbzip2 \
  pbzip2 \
  bzip3 \
  gzip \
  pigz \
  lrzip \
  lz4 \
  lzip \
  plzip \
  lzop \
  pixz \
  zstd \
  7zip \
  dar \
  tar \
  rar \
  unrar \
  tarlz \
  zip \
  unzip \
  unar \
  zpaq \
  lhasa \
  unace \
  cabextract

# DEVELOPMENT
nala_install \
  build-essential \
  make \
  cmake \
  clang \
  clang-tidy \
  clang-format \
  clang-tools \
  curl \
  ca-certificates \
  libssl-dev \
  libmagic-dev \
  libmagickwand-dev \
  git \
  default-jdk \
  shellcheck \
  shfmt \
  zeal

# VS CODE
cd /tmp && pwd || echo
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
sudo rm -v /etc/apt/sources.list.d/vscode.*
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -fv packages.microsoft.gpg
sudo nala update
sudo nala install -y code
cd $CWD && pwd || echo

# REMOVE
nala_remove \
  thunderbird \
  vim

# CLEAN
sudo nala autopurge -y

# ENVIRONMENT
echo "
updating /etc/environment:"
grep "JAVA_HOME=" /etc/environment >/dev/null 2>&1 && sudo sed -i '/JAVA_HOME=/d' /etc/environment
sudo bash -c "echo \"JAVA_HOME=$(update-alternatives --list java)\" >> /etc/environment"
cat /etc/environment
echo

# SYSTCTL
function sysctl_add()
{
  grep "$1" /etc/sysctl.conf >/dev/null 2>&1 && sudo sed -i '/'"$1"'/d' /etc/sysctl.conf
  sudo bash -c "echo \"$1 = $2\" >> /etc/sysctl.conf"
}
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

# SERVICES
sudo systemctl enable --now ssh
sudo systemctl --no-pager status ssh
sudo systemctl restart systemd-sysctl
sudo systemctl --no-pager status systemd-sysctl

