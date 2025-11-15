#!/bin/env python
"""
Jakob Janzen
jakob.janzen80@gmail.com
2025-10-31

Firefox performance and privacy tweaks setup script.

"""
import os
import os.path
import sys

FIREFOX_AUTOCONFIG = "/usr/lib/firefox/defaults/pref/autoconfig.js"
FIREFOX_CFG = "/usr/lib/firefox/firefox.cfg"


def elevate_privileges():
    """Elevate privileges using sudo if not running as root."""
    if os.getuid() != 0:
        cmd = ("sudo", sys.executable, *sys.argv)
        os.execvp("sudo", cmd)


def comment(f, text):
    """Write a comment line to the config file."""
    f.write(f"\n// {text}\n")


def lock_pref(f, key, value):
    """Write a lockPref line to the config file."""
    print(f'lockPref("{key}", {value});')
    f.write(f'lockPref("{key}", {value});\n')


def firefox_autoconfig_setup(config):
    """Setup Firefox autoconfig files."""
    with open(config, "w", encoding="utf-8") as f:
        firefox_cfg = os.path.basename(FIREFOX_CFG)
        f.write(f'pref("general.config.filename", "{firefox_cfg}");\n')
        f.write('pref("general.config.obscure_value", 0);\n')


def firefox_cfg_setup(config):
    """Setup Firefox cfg file."""
    with open(config, "w", encoding="utf-8") as f:
        true, false = "true", "false"
        comment(f, "Firefox configuration file")

        comment(f, "General tweaks")
        lock_pref(f, "network.captive-portal-service.enabled", false)
        lock_pref(f, "network.notify.checkForProxies", false)

        comment(f, "Browser cache")
        lock_pref(f, "browser.cache.disk.parent_directory", '"/dev/shm/ffcache"')
        lock_pref(f, "browser.cache.disk.capacity", 8192000)
        lock_pref(f, "browser.cache.disk.smart_size.enabled", false)
        lock_pref(f, "browser.frecency_half_life_hours", 18)
        lock_pref(f, "browser.max_shutdown_io_lag", 16)
        lock_pref(f, "browser.cache.memory.capacity", 2097152)
        lock_pref(f, "browser.cache.memory.max_entry_size", 327680)
        lock_pref(f, "browser.cache.disk.metadata_memory_limit", 15360)

        comment(f, "GFX rendering tweaks")
        lock_pref(f, "gfx.canvas.accelerated", true)
        lock_pref(f, "gfx.canvas.accelerated.cache-items", 32768)
        lock_pref(f, "gfx.canvas.accelerated.cache-size", 4096)
        lock_pref(f, "gfx.content.skia-font-cache-size", 80)
        lock_pref(f, "gfx.webrender.all", true)
        lock_pref(f, "gfx.webrender.compositor", true)
        lock_pref(f, "gfx.webrender.compositor.force-enabled", true)
        lock_pref(f, "gfx.webrender.enabled", true)
        lock_pref(f, "gfx.webrender.precache-shaders", true)
        lock_pref(f, "gfx.webrender.program-binary-disk", true)
        lock_pref(f, "gfx.webrender.software.opengl", true)
        lock_pref(f, "image.cache.size", 10485760)
        lock_pref(f, "image.mem.decode_bytes_at_a_time", 65536)
        lock_pref(f, "image.mem.shared.unmap.min_expiration_ms", 120000)
        lock_pref(f, "layers.acceleration.force-enabled", true)
        lock_pref(f, "layers.gpu-process.enabled", true)
        lock_pref(f, "layers.gpu-process.force-enabled", true)
        lock_pref(f, "layers.mlgpu.enabled", true)
        lock_pref(f, "media.ffmpeg.vaapi.enabled", true)
        lock_pref(f, "media.gpu-process-decoder", true)
        lock_pref(f, "media.memory_cache_max_size", 1048576)
        lock_pref(f, "media.memory_caches_combined_limit_kb", 3145728)
        lock_pref(f, "media.hardware-video-decoding.force-enabled", true)
        lock_pref(f, "webgl.force-enabled", true)
        lock_pref(f, "webgl.msaa-force", true)
        lock_pref(f, "webgl.max-size", 16384)
        lock_pref(f, "dom.webgpu.enabled", true)


        comment(f, "Increase predictive network operations")
        lock_pref(f, "network.dns.disablePrefetchFromHTTPS", false)
        lock_pref(f, "network.dnsCacheEntries", 20000)
        lock_pref(f, "network.dnsCacheExpiration", 3600)
        lock_pref(f, "network.dnsCacheExpirationGracePeriod", 240)
        lock_pref(f, "network.predictor.enable-hover-on-ssl", true)
        lock_pref(f, "network.predictor.enable-prefetch", true)
        lock_pref(f, "network.predictor.preconnect-min-confidence", 20)
        lock_pref(f, "network.predictor.prefetch-force-valid-for", 3600)
        lock_pref(f, "network.predictor.prefetch-min-confidence", 30)
        lock_pref(f, "network.predictor.prefetch-rolling-load-count", 120)
        lock_pref(f, "network.predictor.preresolve-min-confidence", 10)

        comment(f, "Faster SSL")
        lock_pref(f, "network.ssl_tokens_cache_capacity", 32768)

        comment(f, "Disable network seperations")
        lock_pref(f, "fission.autostart", false)
        lock_pref(f, "privacy.partition.network_state", false)

        comment(f, "Reduce the number of processes")
        lock_pref(f, "dom.ipc.processCount", 1)
        lock_pref(f, "dom.ipc.processCount.webIsolated", 1)

        comment(f, "Enable HTTP pipelining")
        lock_pref(f, "network.http.pipelining", true)
        lock_pref(f, "network.http.proxy.pipelining", true)
        lock_pref(f, "network.http.proxy.pipelining.ssl", true)
        lock_pref(f, "network.http.pipelining.maxrequests", 25)

        comment(f, "Reduce initial paint delay")
        lock_pref(f, "nglayout.initialpaint.delay", 0)
        lock_pref(f, "nglayout.initialpaint.delay_in_oopif", 0)

        comment(f, "DNS and TRR settings")
        lock_pref(f, "network.dns.disableIPv6", true)
        lock_pref(f, "network.trr.mode", 2)

        comment(f, "Privacy enhancements")
        lock_pref(f, "network.http.http3.enabled", true)
        lock_pref(f, "network.http.referer.XOriginPolicy", 2)
        lock_pref(f, "network.http.referer.XOriginTrimmingPolicy", 2)
        lock_pref(f, "toolkit.telemetry.enabled", false)
        lock_pref(f, "datareporting.healthreport.uploadEnabled", false)

        comment(f, "Connection limits")
        lock_pref(f, "network.http.speculative-parallel-limit", 16)
        lock_pref(f, "network.http.max-persistent-connections-per-server", 10)
        lock_pref(f, "network.http.max-connections", 1800)

        comment(f, "User interface preferences")
        lock_pref(f, "ui.prefersReducedMotion", 1)
        lock_pref(f, "browser.uidensity", 1)
        lock_pref(f, "browser.compactmode.show", true)
        lock_pref(f, "toolkit.cosmeticAnimations.enabled", false)
        lock_pref(f, "browser.ml.enable", false)
        lock_pref(f, "browser.ml.chat.enabled", false)
        lock_pref(f, "browser.ml.chat.menu", false)
        lock_pref(f, "browser.tabs.groups.smart.enabled", false)
        lock_pref(f, "browser.ml.linkPreview.enabled", false)

        comment(f, "Media preferences")
        lock_pref(f, "media.peerconnection.enabled", false)
        lock_pref(f, "media.autoplay.default", 2)


def main():
    """Main function."""
    elevate_privileges()
    print(f"UID: {os.getuid()}")

    firefox_autoconfig_setup(FIREFOX_AUTOCONFIG)

    firefox_cfg_setup(FIREFOX_CFG)


if __name__ == "__main__":
    main()
