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


def main():
    """Main function."""
    elevate_privileges()
    print(f"UID: {os.getuid()}")

    with open(FIREFOX_AUTOCONFIG, "w", encoding="utf-8") as f:
        firefox_cfg = os.path.basename(FIREFOX_CFG)
        f.write(f'pref("general.config.filename", "{firefox_cfg}");\n')
        f.write('pref("general.config.obscure_value", 0);\n')

    def lock_pref(key, value):
        """Write a lockPref line to the config file."""
        print(f'lockPref("{key}", {value});')
        f.write(f'lockPref("{key}", {value});\n')

    with open(FIREFOX_CFG, "w", encoding="utf-8") as f:
        # pylint: disable=C3001
        comment = lambda text: f.write(f"// {text}\n")

        comment("")
        comment("Firefox configuration file")
        comment("\n")

        comment("General tweaks")
        lock_pref("network.captive-portal-service.enabled", "false")
        lock_pref("network.notify.checkForProxies", "false")

        comment("Browser cache")
        lock_pref("browser.cache.disk.parent_directory", '"/dev/shm/ffcache"')
        lock_pref("browser.cache.disk.capacity", 8192000)
        lock_pref("browser.cache.disk.smart_size.enabled", "false")
        lock_pref("browser.frecency_half_life_hours", 18)
        lock_pref("browser.max_shutdown_io_lag", 16)
        lock_pref("browser.cache.memory.capacity", 2097152)
        lock_pref("browser.cache.memory.max_entry_size", 327680)
        lock_pref("browser.cache.disk.metadata_memory_limit", 15360)

        comment("GFX rendering tweaks")
        lock_pref("gfx.canvas.accelerated", "true")
        lock_pref("gfx.canvas.accelerated.cache-items", 32768)
        lock_pref("gfx.canvas.accelerated.cache-size", 4096)
        lock_pref("layers.acceleration.force-enabled", "true")
        lock_pref("gfx.content.skia-font-cache-size", 80)
        lock_pref("gfx.webrender.all", "true")
        lock_pref("gfx.webrender.compositor", "true")
        lock_pref("gfx.webrender.compositor.force-enabled", "true")
        lock_pref("gfx.webrender.enabled", "true")
        lock_pref("gfx.webrender.precache-shaders", "true")
        lock_pref("gfx.webrender.program-binary-disk", "true")
        lock_pref("gfx.webrender.software.opengl", "true")
        lock_pref("image.mem.decode_bytes_at_a_time", 65536)
        lock_pref("image.mem.shared.unmap.min_expiration_ms", 120000)
        lock_pref("layers.gpu-process.enabled", "true")
        lock_pref("layers.gpu-process.force-enabled", "true")
        lock_pref("image.cache.size", 10485760)
        lock_pref("media.memory_cache_max_size", 1048576)
        lock_pref("media.memory_caches_combined_limit_kb", 3145728)
        lock_pref("media.hardware-video-decoding.force-enabled", "true")
        lock_pref("media.ffmpeg.vaapi.enabled", "true")

        comment("Increase predictive network operations")
        lock_pref("network.dns.disablePrefetchFromHTTPS", "false")
        lock_pref("network.dnsCacheEntries", 20000)
        lock_pref("network.dnsCacheExpiration", 3600)
        lock_pref("network.dnsCacheExpirationGracePeriod", 240)
        lock_pref("network.predictor.enable-hover-on-ssl", "true")
        lock_pref("network.predictor.enable-prefetch", "true")
        lock_pref("network.predictor.preconnect-min-confidence", 20)
        lock_pref("network.predictor.prefetch-force-valid-for", 3600)
        lock_pref("network.predictor.prefetch-min-confidence", 30)
        lock_pref("network.predictor.prefetch-rolling-load-count", 120)
        lock_pref("network.predictor.preresolve-min-confidence", 10)

        comment("Faster SSL")
        lock_pref("network.ssl_tokens_cache_capacity", 32768)

        comment("Disable network seperations")
        lock_pref("fission.autostart", "false")
        lock_pref("privacy.partition.network_state", "false")

        comment("Reduce the number of processes")
        lock_pref("dom.ipc.processCount", 1)
        lock_pref("dom.ipc.processCount.webIsolated", 1)

        comment("Enable WebGL optimizations")
        lock_pref("webgl.force-enabled", "true")
        lock_pref("webgl.msaa-force", "true")

        comment("Enable HTTP pipelining")
        lock_pref("network.http.pipelining", "true")
        lock_pref("network.http.proxy.pipelining", "true")
        lock_pref("network.http.proxy.pipelining.ssl", "true")
        lock_pref("network.http.pipelining.maxrequests", 25)

        comment("Reduce initial paint delay")
        lock_pref("nglayout.initialpaint.delay", 0)
        lock_pref("nglayout.initialpaint.delay_in_oopif", 0)

        comment("Disable IPv6 DNS lookups")
        lock_pref("network.dns.disableIPv6", "true")

        comment("Privacy enhancements")
        lock_pref("network.http.http3.enabled", "true")
        lock_pref("network.http.referer.XOriginPolicy", 2)
        lock_pref("network.http.referer.XOriginTrimmingPolicy", 2)
        lock_pref("toolkit.telemetry.enabled", "false")
        lock_pref("datareporting.healthreport.uploadEnabled", "false")

        comment("Connection limits")
        lock_pref("network.http.speculative-parallel-limit", 16)
        lock_pref("network.http.max-persistent-connections-per-server", 10)
        lock_pref("network.http.max-connections", 900)

        comment("User interface preferences")
        lock_pref("ui.prefersReducedMotion", 1)
        lock_pref("browser.uidensity", 1)

        comment("Media preferences")
        lock_pref("media.peerconnection.enabled", "false")
        lock_pref("media.autoplay.default", 2)


if __name__ == "__main__":
    main()
