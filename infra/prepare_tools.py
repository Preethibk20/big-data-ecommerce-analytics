"""Prepare shared tool files inside a Docker volume (avoids Windows MAX_PATH and symlink issues)."""
import json
import subprocess
from pathlib import Path

from fetch_tools import main as fetch_verified

ROOT = Path(__file__).resolve().parent.parent
JAVA_IMAGE = "eclipse-temurin:8-jdk-jammy@sha256:a42a161e0edc7f0d3815bcfa22ce6d969fb48f69d0d17d4a1affd9800b455385"
NODE_IMAGE = "python:3.11-bookworm@sha256:5887f265d8d44d8b4734d3658b21d668edf5aaf92e4945bc0c984afbfab105d3"
TOOLS_VOLUME = "ecommerce_cluster_tools"


def main():
    fetch_verified()
    subprocess.run(["docker", "volume", "create", TOOLS_VOLUME], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["docker", "pull", NODE_IMAGE], check=True)
    check = subprocess.run(
        ["docker", "run", "--rm", "-v", f"{TOOLS_VOLUME}:/opt_out:ro", NODE_IMAGE, "test", "-f", "/opt_out/READY.json"],
        check=False,
    )
    if check.returncode == 0:
        print(f"Shared verified tools already prepared in Docker volume {TOOLS_VOLUME}")
        return

    subprocess.run(["docker", "pull", JAVA_IMAGE], check=True)
    subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{TOOLS_VOLUME}:/opt_out",
            JAVA_IMAGE,
            "bash", "-lc", "rm -rf /opt_out/java && cp -a /opt/java/openjdk /opt_out/java",
        ],
        check=True,
    )

    ready_json = json.dumps({"java_image": JAVA_IMAGE, "hadoop": "2.10.2", "pig": "0.17.0", "hive": "2.3.9"}, indent=2)
    extract_script = (
        "set -euo pipefail\n"
        "rm -rf /opt_out/hadoop /opt_out/hive /opt_out/pig /opt_out/READY.json\n"
        "tar -xzf /src_infra/downloads/hadoop-2.10.2.tar.gz -C /opt_out && mv /opt_out/hadoop-2.10.2 /opt_out/hadoop\n"
        "tar -xzf /src_infra/downloads/apache-hive-2.3.9-bin.tar.gz -C /opt_out && mv /opt_out/apache-hive-2.3.9-bin /opt_out/hive\n"
        "tar -xzf /src_infra/downloads/pig-0.17.0.tar.gz -C /opt_out && mv /opt_out/pig-0.17.0 /opt_out/pig\n"
        "cp -f /src_infra/hadoop/* /opt_out/hadoop/etc/hadoop/\n"
        "cp -f /src_infra/hive-site.xml /opt_out/hive/conf/hive-site.xml\n"
        f"cat <<'EOF' > /opt_out/READY.json\n{ready_json}\nEOF\n"
    )
    subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{TOOLS_VOLUME}:/opt_out",
            "-v", f"{(ROOT / 'infra').resolve()}:/src_infra:ro",
            NODE_IMAGE,
            "bash", "-lc", extract_script,
        ],
        check=True,
    )
    print(f"Shared verified tools prepared in Docker volume {TOOLS_VOLUME}")


if __name__ == "__main__":
    main()
