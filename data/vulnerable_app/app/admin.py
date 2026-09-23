"""Admin utilities."""
import os
import subprocess


def ping_host(host):
    return os.system(f"ping -c 1 {host}")


def run_backup(target):
    return subprocess.run(["/usr/local/bin/backup", "--target", target], check=True, capture_output=True)


def disk_report(path):
    return subprocess.check_output("du -sh " + path, shell=True)
