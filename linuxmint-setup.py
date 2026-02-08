#!/bin/env python
"""
Jakob Janzen
jakob.janzen80@gmail.com
2026-02-22

Linux Mint setup script.
"""
import os
import sys
import argparse
import subprocess
import urllib.request
import shutil
import re


class Logger:
    RED = "\033[1;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def section(self, message):
        print(f"\n\n{self.BLUE}[[ {message.upper()} ]]{self.RESET}")

    def subsection(self, message):
        print(f"\n{self.CYAN}[ {message} ]{self.RESET}")

    def step(self, message):
        print(f"  {self.WHITE}{self.BOLD}->{self.RESET} {message}...")

    def info(self, message):
        print(f"{self.GREEN}INFO:{self.RESET} {message}.")

    def success(self, message):
        print(f"{self.GREEN}{self.BOLD}* SUCCESS:{self.RESET} {message}.")

    def warning(self, message):
        print(f"{self.YELLOW}WARNING:{self.RESET} {message}?", file=sys.stderr)

    def error(self, message):
        print(f"{self.RED}{self.BOLD}ERROR:{self.RESET} {message}!", file=sys.stderr)


class Setup(object):
    def __init__(self, logger):
        self.parser = argparse.ArgumentParser(
            description=f"Usage: {os.path.basename(sys.argv[0])} [OPTIONS]",
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=False,
        )
        self.options = [
            ["u", "update", "store_true", "Update only system."],
            ["r", "remove", "store_true", "Remove only packages."],
            ["i", "install", "store_true", "Install only packages."],
            [None, "vscode", "store_true", "Add repository and install VS Code."],
            ["c", "clean", "store_true", "Clean only packages."],
            ["s", "system", "store_true", "Setup system settings."],
            ["h", "help", "help", "Show this help and quit."],
        ]
        self.logger = logger

    def _add_argument(self, short, long, action, help_text):
        flags = [f"-{short}" if short else None, f"--{long}"]
        flags = [f for f in flags if f]
        self.parser.add_argument(*flags, action=action, help=help_text)

    def elevate_privileges(self):
        """Elevate privileges using sudo if not running as root."""
        self.logger.info(f"Current UID: {os.getuid()}")
        if os.getuid() != 0:
            self.logger.subsection("Elevating privileges to ROOT")
            cmd = ("sudo", sys.executable, *sys.argv)
            try:
                os.execvp("sudo", cmd)
            except Exception as e:
                self.logger.error(f"Failed to elevate privileges: {e}")
                sys.exit(1)

    def run_as_user(self, cmd, check=True):
        """
        Runs any command as the original logged-in user.
        If not running under sudo, it runs as the current user.
        """
        original_user = os.environ.get("SUDO_USER")
        if original_user and os.getuid() == 0:
            self.logger.info(f"Running '{cmd[0]}' as user: {original_user}")
            full_cmd = ["sudo", "-u", original_user] + cmd
        else:
            full_cmd = cmd
        try:
            return subprocess.run(full_cmd, check=check)
        except subprocess.CalledProcessError as e:
            self.logger.error(
                f"Execution failed for '{cmd[0]}'. Exit code: {e.returncode}"
            )
            return None

    def cli_options(self):
        for option in self.options:
            self._add_argument(*option)
        return self.parser.parse_args()

    def check_argv(self, argv):
        self.logger.step("Checking if CLI options were given")
        if len(argv) == 1:
            self.parser.print_help()
            sys.exit(1)
        self.logger.success(f"{len(argv)-1} given")

    def update(self):
        self.logger.subsection("System Refresh")
        self.logger.step("Updating APT cache")
        subprocess.run(["apt", "update", "-y"])
        self.logger.step("Ensuring Nala is installed")
        subprocess.run(["apt", "install", "-y", "nala"])
        self.logger.step("Syncing Nala with repositories")
        subprocess.run(["nala", "update"])
        self.logger.success("System repositories are up to date")

    def upgrade(self):
        self.update()
        self.logger.subsection("Full System Upgrade")
        self.logger.step("Running Nala upgrade")
        subprocess.run(["nala", "upgrade", "-y"])
        self.logger.success("All system packages are current")

    def remove(self, categories=None):
        if categories:
            for key, packages in categories.items():
                self.logger.subsection(f"Removing Category: {key}")
                self.logger.step(f"Purging {len(packages)} packages")
                subprocess.run(["nala", "purge", "-y"] + packages)
                self.logger.success(f"Removed all packages in {key}")

    def install(self, categories=None):
        if categories:
            for key, packages in categories.items():
                self.logger.subsection(f"Installing Category: {key}")
                self.logger.step(f"Installing {len(packages)} packages from {key}")
                subprocess.run(["nala", "install", "-y"] + packages)
                self.logger.success(f"Category {key} installed successfully")

    def clean(self):
        self.logger.step("Autoremoving")
        subprocess.run(["nala", "autoremove"])
        self.logger.step("Autopurging")
        subprocess.run(["nala", "autopurge"])
        self.logger.step("Cleaning")
        subprocess.run(["nala", "clean"])

    def install_vscode(self):
        self.logger.subsection("VS Code Repository & Key Setup")
        keyring_dir = "/etc/apt/keyrings"
        keyring_path = f"{keyring_dir}/packages.microsoft.gpg"
        repo_path = "/etc/apt/sources.list.d/vscode.list"
        self.logger.step("Purging old Microsoft repository and key files")
        conflicting_files = [
            repo_path,
            "/etc/apt/sources.list.d/vscode.list.save",
            "/etc/apt/sources.list.d/vscode.sources",
            "/usr/share/keyrings/microsoft.gpg",
            "/usr/share/keyrings/gpgsecurity.microsoft.com.gpg",
            "/etc/apt/trusted.gpg.d/microsoft.gpg",
            keyring_path,
        ]
        for f in conflicting_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                    self.logger.info(f"Removed conflicting file: {f}")
                except Exception as e:
                    self.logger.error(f"Could not remove {f}: {e}")
        try:
            os.makedirs(keyring_dir, exist_ok=True)
            self.logger.step("Downloading fresh GPG key from Microsoft")
            url = "https://packages.microsoft.com/keys/microsoft.asc"
            with urllib.request.urlopen(url) as response:
                asc_data = response.read()
            gpg_result = subprocess.run(
                ["gpg", "--dearmor"], input=asc_data, capture_output=True, check=True
            )
            with open(keyring_path, "wb") as f:
                f.write(gpg_result.stdout)
            os.chmod(keyring_path, 0o644)
            self.logger.info(f"GPG key successfully installed to {keyring_path}")
            self.logger.step("Creating clean repository list")
            repo_entry = (
                f"deb [arch=amd64 signed-by={keyring_path}] "
                "https://packages.microsoft.com/repos/code stable main\n"
            )
            with open(repo_path, "w") as f:
                f.write(repo_entry)
            self.logger.step("Clearing local APT lists for fresh sync")
            subprocess.run(["rm", "-rf", "/var/lib/apt/lists/*"], check=True)
            self.logger.step("Running Nala update and installing 'code'")
            subprocess.run(["nala", "update"], check=True)
            subprocess.run(["nala", "install", "-y", "code"], check=True)
            self.logger.success("VS Code installed successfully")
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")

    def apply_sysctl_optimizations(self):
        """Applies kernel and virtual memory optimizations for laptop stability."""
        self.logger.subsection("Kernel & VM Optimizations")
        target_file = "/etc/sysctl.d/99-zzz-sysctl.conf"
        sysctl_content = (
            "# Optimized sysctl settings for TUXEDO Laptop\n"
            "kernel.printk = 3 4 1 3\n"
            "kernel.sysrq = 0\n"
            "\n"
            "vm.dirty_background_ratio = 2\n"
            "vm.dirty_ratio = 60\n"
            "vm.swappiness = 10\n"
        )
        try:
            self.logger.step(f"Writing optimizations to {target_file}")
            with open(target_file, "w") as f:
                f.write(sysctl_content)
            os.chmod(target_file, 0o644)
            self.logger.step("Reloading sysctl configuration")
            subprocess.run(["sysctl", "--system"], check=True, capture_output=True)
            self.logger.success("Kernel and VM parameters applied successfully")
        except Exception as e:
            self.logger.error(f"Failed to apply sysctl settings: {e}")

    def set_journald_property(self, key, value):
        config_file = "/etc/systemd/journald.conf"
        backup_file = f"{config_file}.bak"
        val_regex = r"(^[0-9]+[KMGTPsmhday]?$)|(^(persistent|auto|volatile|yes|no)$)"
        if not re.match(val_regex, str(value)):
            self.logger.error(f"Invalid value '{value}' for key '{key}'")
            return False
        try:
            if not os.path.exists(backup_file):
                shutil.copy2(config_file, backup_file)
                self.logger.info(f"Backup created: {backup_file}")
            with open(config_file, "r") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                stripped = line.strip()
                if not (
                    stripped.startswith(f"{key}=") or stripped.startswith(f"#{key}=")
                ):
                    new_lines.append(line)
            final_lines = []
            found_section = False
            for line in new_lines:
                final_lines.append(line)
                if "[Journal]" in line:
                    final_lines.append(f"{key}={value}\n")
                    found_section = True
            if not found_section:
                final_lines.insert(0, f"[Journal]\n{key}={value}\n")
            with open(config_file, "w") as f:
                f.writelines(final_lines)
            self.logger.step(f"Journald: {key} set to {value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify journald.conf: {e}")
            return False

    def activate_service(self, service_name):
        """Enable, start, and restart a systemd service, then show status."""
        self.logger.step(f"Activating service: {service_name}")
        try:
            subprocess.run(["systemctl", "enable", "--now", service_name], check=True)
            subprocess.run(["systemctl", "restart", service_name], check=True)
            self.logger.info(f"Verifying status for {service_name}")
            status = subprocess.run(
                ["systemctl", "--no-pager", "status", service_name, "-n", "0"],
                capture_output=True,
                text=True,
            )
            if status.returncode == 0:
                self.logger.success(f"Service {service_name} is active and enabled")
            else:
                self.logger.warning(
                    f"Service {service_name} started but status reported issues"
                )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to activate service {service_name}: {e}")


def main():
    logger = Logger()
    setup = Setup(logger=logger)
    args = setup.cli_options()
    setup.check_argv(sys.argv)
    setup.elevate_privileges()

    if args.update:
        logger.section("UPDATE")
        setup.upgrade()
        logger.success("System is up to date")

    if args.remove:
        logger.section("REMOVE")
        setup.update()
        categories = {
            "VIM": [
                "vim-common",
                "vim-tiny",
            ],
            "OTHER": [
                "gcolor3",
            ],
        }
        setup.remove(categories)
        logger.success("Removed packages from system")

    if args.install:
        logger.section("INSTALL")
        setup.update()
        categories = {
            "APT": [
                # 1. System Core & Base Utilities
                "ubuntu-standard",  # Essential base system utilities
                "apt-transport-https",  # Legacy support for secure repositories
                # 2. Package Management & GUI
                "aptitude",  # Powerful CLI terminal interface for APT
                "synaptic",  # Reliable GUI package manager (GTK-based)
                # 3. Automation & Maintenance
                "unattended-upgrades",  # Automatic installation of security updates
                # 4. User Experience & Codecs
                "ubuntu-restricted-extras",  # Media codecs, fonts, and restricted software
            ],
            "PACKAGE_TOOLS": [
                # 1. Repository & Connectivity Infrastructure
                "apt-transport-https",  # Legacy support for HTTPS repositories
                "bash-completion",  # Tab-completion for package names in terminal
                "ca-certificates",  # Required for secure GPG/Repo downloads
                "software-properties-common",  # Provides 'add-apt-repository' for VS Code/TUXEDO
                # 2. Advanced Management Frontends
                "nala",  # Your primary, faster terminal frontend
                "synaptic",  # The "gold standard" GUI for complex fixes
                "apt-file",  # Search for which package contains a missing file
                # 3. Python Integration (For your script)
                "python3-apt",  # Allows Python to check package status directly
                # 4. Post-Install & Maintenance
                "needrestart",  # Alerts you which services need a restart after updates
                "ppa-purge",  # Safely rolls back PPA conflicts
                "deborphan",  # Finds leftover libraries from your Cinnamon purge
            ],
            "REQUIRED": [
                # 1. Hardware & Thermal Management
                "thermald",  # Intel Thermal Daemon (Essential for TUXEDO laptops)
                "smartmontools",  # SSD Health and Monitoring
                # 2. Background System Optimization
                "haveged",  # Entropy generator (Prevents system lag)
                "preload",  # Adaptive readahead (Speeds up app launches)
                # 3. Interactive CLI Tools
                "tmux",  # Terminal multiplexer
                "neovim",  # Extensible text editor
            ],
            "UTILITY": [
                # 1. File Management & Navigation
                "mc",  # Midnight Commander (Classic dual-pane manager)
                "tree",  # Visual directory structure
                "fzf",  # Fuzzy finder (Essential for terminal speed)
                "eza",  # Modern 'ls' replacement with colors/icons
                "zoxide",  # Smart 'cd' replacement (Recommended addition)
                # 2. Disk & System Analysis
                "duf",  # Modern 'df' replacement (Disk usage overview)
                "ncdu",  # Interactive 'du' (Find large folders quickly)
                "gdisk",  # GPT fdisk (Crucial for modern SSD partitioning)
                # 3. Text Processing & Viewing
                "bat",  # Modern 'cat' with syntax highlighting
                "ripgrep",  # Modern 'grep' (Blazing fast)
                "jq",  # JSON processor (Essential for dev work)
                # 4. System Configuration
                "dconf-cli",  # CLI access to system settings
                "dconf-editor",  # GUI access to system settings (The one we used earlier)
            ],
            "ANALYZE": [
                # 1. Real-time System Monitors (Visual)
                "btop",  # Modern, high-detail resource monitor (Your primary)
                "htop",  # The classic standard (Good fallback)
                "nmon",  # Performance monitor for CPU/Disk/Network/NFS
                # 2. Specialized Monitoring
                "iotop",  # Monitor disk I/O per process (Find what's slowing the SSD)
                # 3. Hardware Information
                "hwinfo",  # Detailed hardware identification
                "inxi",  # Powerful system/driver summary (Essential for Mint)
            ],
            "NETWORK": [
                # 1. Critical Infrastructure & Certificates
                "ca-certificates",  # Must be first: validates SSL for all other tools
                "net-tools",  # Provides 'ifconfig' and 'netstat' for diagnostics
                # 2. Data Retrieval & Speed Testing
                "curl",  # Modern transfer tool (Used in your VS Code logic)
                "wget",  # Classic downloader
                "speedtest-cli",  # Quick terminal-based speed checks (Recommended)
                # 3. Secure Shell (SSH) Suite
                "openssh-client",  # To connect to your servers
                "openssh-server",  # To allow remote access to this laptop
                "openssh-sftp-server",  # Secure file transfer support
            ],
            "SPELLING": [
                # 1. Engines & Integration (The "Bridge")
                "libenchant-2-2",  # The bridge between apps and dictionaries
                "hunspell",  # Modern standard engine
                "aspell",  # Classic CLI engine
                # 2. German (DE) Support
                "hunspell-de-de-frami",  # Primary German dictionary
                "aspell-de",  # CLI German dictionary
                "myspell-dictionary-de",  # Legacy German support
                "mythes-de",  # German Thesaurus
                "hyphen-de",  # German Hyphenation
                # 3. English (EN) Support
                "hunspell-en-us",  # Primary English dictionary
                "aspell-en",  # CLI English dictionary
                "mythes-en-us",  # English Thesaurus
                "hyphen-en-us",  # English Hyphenation
            ],
            "ACCESSORY": [
                # 1. System Styling & Theme Consistency (Crucial for XFCE)
                "adwaita-qt",  # Makes Qt5 apps match your GTK theme
                "adwaita-qt6",  # Makes Qt6 apps match your GTK theme
                "qt5ct",  # Qt5 configuration tool (Recommended addition)
                "qt6ct",  # Qt6 configuration tool (Recommended addition)
                # 2. Development & File Utilities
                "meld",  # Visual diff and merge tool (Excellent for dev)
                # 3. Media & Communication
                "cheese",  # Webcam viewer (Perfect for testing hardware)
                "transmission-gtk",  # BitTorrent client (The GTK version fits XFCE)
            ],
            "OFFICE": [
                # 1. LibreOffice Core & UI Integration
                "libreoffice",  # The main office suite
                "libreoffice-gtk3",  # Makes it look native in XFCE
                "libreoffice-style-sifr",  # Clean, flat icon set (Good for XFCE)
                "libreoffice-l10n-de",  # German language pack (Recommended)
                # 2. Document Conversion & Markdown
                "pandoc",  # The "universal" document converter
                # 3. LaTeX / Scientific Publishing (The Heavy Part)
                "texlive-full",  # Complete LaTeX distribution (~5GB)
            ],
            "GRAPHIC": [
                # 1. Raster Image Editing (GIMP Suite)
                "gimp",  # The core image editor
                "gimp-data-extras",  # Additional brushes, gradients, and patterns
                "gimp-plugin-registry",  # Huge collection of essential plugins (Recommended)
                "gimp-help-de",  # German help files (Recommended)
                # 2. Vector Illustration (Inkscape Suite)
                "inkscape",  # The core vector editor
                # 3. Hardware & Library Support
                "libwacom-common",  # Drawing tablet support (Essential for graphics)
            ],
            "MULTIMEDIA": [
                # 1. High-Performance Playback (MPV Suite)
                "mpv",  # Minimalist, high-performance player (Best for Intel)
                "yt-dlp",  # CLI tool to stream/download web video (Recommended)
                # 2. Universal Playback (VLC Suite)
                "vlc",  # The "all-in-one" media player
                "vlc-l10n",  # Language localization for VLC
                "vlc-plugin-pipewire",  # Native PipeWire support (Essential for Mint 22)
                "vlc-plugin-jack",  # Jack audio support
                "vlc-plugin-fluidsynth",  # MIDI playback support
                "vlc-plugin-svg",  # Scalable Vector Graphics support
                "vlc-plugin-visualization",  # Visualizer support
                # 3. Audio Editing & Tools
                "audacity",  # Multi-track audio editor
                "pavucontrol",  # PulseAudio/PipeWire volume control (The Mixer)
            ],
            "CODEC": [
                # 1. Core Framework & Multi-purpose Tools
                "ffmpeg",  # The universal multimedia engine (Must be first)
                "libavif-bin",  # AVIF image format tools
                "libwebm-tools",  # WebM container tools
                "libwebm1",  # WebM shared library
                # 2. Video Encoders (High Performance)
                "dav1d",  # AV1 decoder (Fastest for Intel CPUs)
                "davs2",  # AVS2 video decoder
                "rav1e",  # AV1 encoder
                "svt-av1",  # Intel-optimized AV1 encoder (Best for your CPU)
                "x264",  # Standard H.264 encoder
                "x265",  # Standard H.265/HEVC encoder
                # 3. Audio Encoders
                "aften",  # AC3 audio encoder
                "faac",  # AAC audio encoder
                "fdkaac",  # CLI for FDK AAC
                "libfdk-aac2",  # High-quality AAC library
                "lame",  # Classic MP3 encoder
                "speex",  # Speech-optimized codec
                # 4. Container & Metadata Utilities
                "mkvtoolnix",  # MKV manipulation tools
                "ogmtools",  # OGG/OGM manipulation tools
            ],
            "COMPRESSION": [
                # 1. Core System Standards
                "tar",  # The foundational archiving tool
                "gzip",  # Standard compression
                "bzip2",  # Classic high-compression
                "zip",  # Universal compatibility
                "unzip",  # Universal extraction
                # 2. Parallel & High-Performance (Best for your Intel CPU)
                "pigz",  # Parallel GZIP (Fastest for daily use)
                "pbzip2",  # Parallel BZIP2
                "lbzip2",  # Alternative Parallel BZIP2
                "pixz",  # Parallel XZ
                "zstd",  # Modern, ultra-fast compression (standard for Mint 22)
                "lz4",  # Extreme speed compression
                "lrzip",  # Long-range ZIP (Great for massive files)
                # 3. Modern & Specialized Formats
                "7zip",  # Modern 7z standard
                "zpaq",  # Maximum compression ratio
                "lzip",  # LZMA-based format
                "plzip",  # Parallel LZIP
                "tarlz",  # Tar with LZIP support
                "lzop",  # Fast LZO compression
                # 4. Legacy, Proprietary & Extraction Tools
                "unar",  # The "Universal" extractor (Must-have)
                "unrar",  # For RAR files (Non-free version)
                "rar",  # For creating RAR files
                "cabextract",  # For Windows .cab files
                "lhasa",  # For old .lzh files
                "unace",  # For old .ace files
                "dar",  # Disk Archive (For backups)
                "par2",  # Parchive (For repairing corrupted archives)
            ],
            "DEVELOPMENT_COMPILER": [
                # Build Tools
                "build-essential",  # make, gcc, libc
                "cmake",  # Meta-build system
                "cmake-format",  # Formatter for CMake
                "ninja-build",  # High-performance build tool
                # Clang/LLVM Suite
                "clang",  # Compiler
                "clang-format",  # Formatter
                "clang-tidy",  # Linter
                "clang-tools",  # Extra utilities
                "lldb",  # Debugger
                # Libraries & Analysis
                "libmagic-dev",  # File type identification
                "libmagickwand-dev",  # Image manipulation
                "libssl-dev",  # Crypto/Networking
                "valgrind",  # Memory profiling
            ],
            "DEVELOPMENT_PYTHON": [
                # Environment & Runtime
                "pipx",  # Isolated CLI tool installer (Safe for Mint 22)
                "python-is-python3",  # Symlink provider
                "python3-gpg",  # GPG bindings for your script
                "python3-pip",  # Package installer
                "python3-venv",  # Virtual environments
                # Project Management
                "pipenv",  # Dependency management
                "python3-poetry",  # Modern project management
                # Testing & Linting
                "black",  # Uncompromising formatter
                "python3-autopep8",  # Style guide checker
                "python3-flake8",  # Logic linter
                "python3-pytest",  # Testing framework
            ],
            "DEVELOPMENT_SHELL": [
                "expect",  # Interactive automation
                "shellcheck",  # Script analyzer
                "shfmt",  # Script formatter
            ],
            "DEVELOPMENT_DOCS": [
                "bash-doc",  # Bash manuals
                "linux-doc",  # Kernel documentation
                "python3-doc",  # Python 3 manuals
                "zeal",  # API Documentation browser
            ],
            "DEVELOPMENT_JAVA": [
                "default-jdk",  # Standard OpenJDK
            ],
        }

        setup.install(categories)

        logger.section("FLATPAK MANAGEMENT")
        logger.step("Checking configured remotes")
        setup.run_as_user(["flatpak", "remotes"])
        logger.step("Listing installed flatpaks")
        setup.run_as_user(["flatpak", "list"])

        logger.subsection("Flatpak Update")
        logger.step("Checking for flatpak updates and runtimes")
        setup.run_as_user(["flatpak", "update", "-y"])

        logger.success("All required packages (APT & Flatpak) have been processed")

    if args.vscode:
        logger.section("VISUAL STUDIO CODE")
        setup.update()
        setup.install_vscode()
        logger.success("VS Code installation and repository setup complete")

    if args.clean:
        logger.section("CLEAN")
        setup.update()
        setup.clean()
        logger.success("Cleaned up packages in System")

    if args.system:
        logger.section("SYSCTL")
        setup.apply_sysctl_optimizations()
        logger.section("JOURNALD")
        setup.logger.subsection("Configuring System Journal")
        setup.set_journald_property("Storage", "persistent")
        setup.set_journald_property("SystemMaxUse", "100M")
        setup.set_journald_property("SystemMaxFileSize", "50M")
        setup.set_journald_property("SyncIntervalSec", "5m")
        logger.success("Journald configuration updated")
        logger.section("SERVICES")
        services = [
            "systemd-sysctl",
            "systemd-journald",
            "preload",
            "haveged",
            "ssh",
        ]
        for service in services:
            setup.activate_service(service)
        logger.success("All system services are optimized and running")

    print()


if __name__ == "__main__":
    main()
