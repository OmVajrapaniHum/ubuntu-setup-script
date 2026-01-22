#!/bin/bash
#
# Jakob Janzen
# jakob.janzen80@gmail.com
# 2026-01-18
#
# Linux Mint setup script.
#

export CWD="$PWD"

function usage {
    echo "Usage: $(basename "$0") [OPTIONS]
    -u, --update    Update only system.
    -r, --remove    Remove only packages.
    -i, --install   Install only packages.
        --vscode    Add repository and install VS Code.
    -c, --clean     Clean only packages.
    -s, --system    Update system settings.
    -h, --help      Show this help and quit.
    "
    exit 1
}

TEMP=$(getopt -o 'uricsh' --long 'update,remove,install,vscode,clean,system,help' -- "$@")
if [[ $? -ne 0 ]]; then
    usage
fi
eval set -- "$TEMP"
unset TEMP

SETUP=
while true; do
    case "$1" in
        '-u' | '--update')
            SETUP=update_packages
            shift
            continue
            ;;

        '-r' | '--remove')
            SETUP=remove_packages
            shift
            continue
            ;;

        '-i' | '--install')
            SETUP=install_packages
            shift
            continue
            ;;

        '--vscode')
            SETUP=install_vscode
            shift
            continue
            ;;

        '-c' | '--clean')
            SETUP=clean_packages
            shift
            continue
            ;;

        '-s' | '--system')
            SETUP=system
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

function section {
    echo "

[ $1 ]"
}

function step {
    echo "
* $1 ..."
}

function update {
    step "apt update"
    sudo apt update -y

    step "apt install nala"
    sudo apt install -y nala

    step "nala update"
    sudo nala update
}

function upgrade {
    update

    step "apt upgrade"
    sudo apt upgrade -y

    step "nala upgrade"
    sudo nala upgrade -y
}

function nala_install {
    step "$1"
    shift
    if [[ -n "$(echo $@|xargs)" ]]; then
        sudo nala install $@
    fi
}

function nala_remove {
    if [[ -n "$(echo $@|xargs)" ]]; then
        sudo nala purge $@
    fi
}

function activate_service {
    step "activate service $1"
    sudo systemctl enable --now $1
    sudo systemctl restart $1
    sudo systemctl --no-pager status $1
}

case $SETUP in
    update_packages)
        section "UPDATE"

        upgrade
        ;;

    remove_packages)
        PKG_REMOVE='
            vim-common
            vim-tiny
            '

        section "REMOVE"

        update
        nala_remove $PKG_REMOVE
        ;;

    install_packages)
        section "INSTALL"

        update

        step "install packages"

        nala_install "apt" \
            ubuntu-restricted-extras \
            unattended-upgrades \
            ubuntu-standard \
            aptitude \
            apt-transport-https

        nala_install "required" \
            neovim \
            preload \

        nala_install "utility" \
            duf \
            gdisk \
            tree \
            dconf-cli \
            dconf-editor

        nala_install "monitor" \
            btop \
            htop \
            hwinfo \
            iotop \
            nmon

        nala_install "network" \
            ca-certificates \
            curl \
            net-tools \
            openssh-client \
            openssh-server \
            openssh-sftp-server \
            wget

        nala_install "spelling" \
            aspell \
            aspell-de \
            aspell-en \
            hunspell \
            hunspell-de-de-frami \
            hunspell-en-us \
            myspell-dictionary-de \
            hyphen-en-us \
            hyphen-de \
            mythes-en-us \
            mythes-de

        nala_install "accessory" \
            cheese \
            gcolor3 \
            meld \
            transmission

        nala_install "office" \
            libreoffice \
            libreoffice-style-sifr \
            pandoc \
            texlive-full

        nala_install "graphic" \
            gimp \
            gimp-data-extras \
            inkscape

        nala_install "multimedia" \
            mpv \
            vlc \
            vlc-l10n \
            vlc-plugin-fluidsynth \
            vlc-plugin-jack \
            vlc-plugin-pipewire \
            vlc-plugin-svg \
            vlc-plugin-visualization

        nala_install "codec" \
            aften \
            dav1d \
            davs2 \
            faac \
            fdkaac \
            ffmpeg \
            lame \
            libavif-bin \
            libfdk-aac2 \
            libwebm-tools \
            libwebm1 \
            mkvtoolnix \
            ogmtools \
            rav1e \
            speex \
            svt-av1 \
            x264 \
            x265

        nala_install "compression" \
            7zip \
            bzip2 \
            bzip3 \
            cabextract \
            dar \
            gzip \
            lbzip2 \
            lhasa \
            lrzip \
            lz4 \
            lzip \
            lzop \
            par2 \
            pbzip2 \
            pigz \
            pixz \
            plzip \
            rar \
            tar \
            tarlz \
            unace \
            unar \
            unrar \
            unzip \
            zip \
            zpaq \
            zstd

        nala_install "development compiler" \
            build-essential \
            cmake \
            cmake-format \
            git \
            clang \
            clang-format \
            clang-tidy \
            clang-tools \
            libmagic-dev \
            libmagickwand-dev \
            libssl-dev \
            valgrind \

        nala_install "development shell" \
            shellcheck \
            shfmt

        nala_install "development python" \
            black \
            pipenv \
            python-is-python3 \
            python3-autopep8 \
            python3-flake8 \
            python3-gpg \
            python3-pip \
            python3-poetry \
            python3-pytest \
            python3-venv

        nala_install "development java" \
            default-jdk

        nala_install "documentation" \
            zeal

        step "update flatpak packages"
        flatpak remotes
        flatpak list
        flatpak update
        ;;

    install_vscode)
        section "INSTALL VSCODE"

        step "current working directory"
        pwd
        CWD=$PWD

        step "go to temporary directory"
        cd /tmp && pwd || echo

        step "get GPG key for VS Code repository"
        wget -qO- https://packages.microsoft.com/keys/microsoft.asc | \
        gpg --dearmor >packages.microsoft.gpg
        ls -l packages.microsoft.gpg

        step "install GPG key for VS Code in keyring"
        sudo install -D -o root -g root -m 644 packages.microsoft.gpg \
        /etc/apt/keyrings/packages.microsoft.gpg

        step "prepare and create VS Code repository"
        sudo rm -v /etc/apt/sources.list.d/vscode.*
        echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/packages.microsoft.gpg] " \
        "https://packages.microsoft.com/repos/code stable main" | \
        sudo tee /etc/apt/sources.list.d/vscode.list

        step "remove temporary VS Code GPG key"
        rm -fv packages.microsoft.gpg

        step "install VS Code"
        update
        sudo nala install -y code

        step "go back to current working directory"
        cd $CWD && pwd || echo
        ;;

    clean_packages)
        section "CLEAN"

        update

        step "autopurge packages"
        sudo nala autopurge -y
        sudo apt autopurge -y
        ;;

    system)
        section "SYSCTL"

        src=$(mktemp)
        trg="/etc/sysctl.d/99-zzz-sysctl.conf"
        sudo echo '
kernel.printk = 3 4 1 3
kernel.sysrq = 0

vm.dirty_background_ratio = 2
vm.dirty_ratio = 60
vm.swappiness = 10
        ' >$src
        sudo cp -fv $src $trg
        rm -v $src
        sudo sysctl --system
exit
        section "DNS"

#        src="$(mktemp)"
#        trgdir="/etc/systemd/resolved.conf.d"
#        trg="$trgdir/99-custom.conf"
#        echo "[Resolve]
#DNS=1.1.1.1#cloudflare-dns.com 1.0.0.1#cloudflare-dns.com 2606:4700:4700::1111#cloudflare-dns.com 2606:4700:4700::1001#cloudflare-dns.com
#FallbackDNS=8.8.8.8#dns.google 8.8.4.4#dns.google 2001:4860:4860::8888#dns.google 2001:4860:4860::8844#dns.google
#        " >$src
#
#        step "ensure configurations directory $trgdir"
#        sudo mkdir -pv $trgdir
#        sudo ls -l $trgdir
#
#        step "apply configuration $trg"
#        sudo cp -fv $src $trg
#        sudo chmod 644 $trg
#
#        step "new configuration $trg"
#        sudo cat $trg
#        rm -v $src
#
#        section "SERVICES"


        activate_service systemd-sysctl
#        enable_service systemd-resolved
        activate_service preload
        activate_service ssh
#        enable_service NetworkManager
#        enable_service ModemManager

#        step "link generated resolv file global"
#        src="/run/systemd/resolve/resolv.conf"
#        trg="/etc/resolv.conf"
#        sudo ln -sfv $src $trg

#        step "check link"
#        sudo ls -l $trg
#        sudo systemctl restart systemd-networkd

#        step "reduce display effects"
#        gsettings describe org.gnome.desktop.interface enable-animations
#        gsettings get org.gnome.desktop.interface enable-animations
#        gsettings set org.gnome.desktop.interface enable-animations false
#        gsettings get org.gnome.desktop.interface enable-animations
        ;;

esac

echo
exit
