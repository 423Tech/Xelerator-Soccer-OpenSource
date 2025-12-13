#!/bin/bash
set -euo pipefail
# Generic wrapper: uses $HOME and $USER so same script works for different accounts
# If run from systemd with User=..., HOME and USER are set appropriately.

# Source user's bashrc if present (allows custom PATH / pyenv / rossetup)
if [ -n "${HOME-}" ] && [ -f "${HOME}/.bashrc" ]; then
  # shellcheck disable=SC1090
  source "${HOME}/.bashrc"
fi

# Try common ROS distro install locations (adjust as needed)
for distro in humble rolling foxy galactic iron; do
  if [ -f "/opt/ros/${distro}/setup.bash" ]; then
    # shellcheck disable=SC1090
    source "/opt/ros/${distro}/setup.bash"
    break
  fi
done

# Source workspace overlays relative to the user's home or project dir
PROJECT_DIR="${HOME}/Xelerator-Soccer-OpenSource"
# Avoid unbound variable errors in setup scripts
export COLCON_TRACE=${COLCON_TRACE:-}
for f in \
  "${PROJECT_DIR}/install/local_setup.bash" \
  "${PROJECT_DIR}/install/setup.bash" \
  "${HOME}/ros2_ws/install/setup.bash"; do
  if [ -f "$f" ]; then
    # Some setup scripts assume variables exist; temporarily disable nounset
    set +u
    # shellcheck disable=SC1090
    source "$f"
    set -u
  fi
done

cd "${PROJECT_DIR}" || exit 1

# ensure domain id (can be overridden by systemd Environment= if needed)
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-99}

# Choose serial port heuristically (prefer ttyUSB1 if present)
if [ -e /dev/sllidar ]; then
  SERIAL_PORT=/dev/sllidar
elif [ -e "${HOME}/dev_sllidar_port" ]; then
  SERIAL_PORT=$(cat "${HOME}/dev_sllidar_port")
elif [ -e /dev/ttyUSB0 ]; then
  SERIAL_PORT=/dev/ttyUSB1
elif [ -e /dev/ttyUSB1 ]; then
  SERIAL_PORT=/dev/ttyUSB0
else
  SERIAL_PORT=${SERIAL_PORT:-/dev/ttyUSB0}
fi

SERIAL_BAUDRATE=${SERIAL_BAUDRATE:-256000}

# Simple probe: wait for device to exist and not be held by another process
PROBE_TIMEOUT=${PROBE_TIMEOUT:-20} # seconds
PROBE_INTERVAL=${PROBE_INTERVAL:-1}
elapsed=0
while [ $elapsed -lt $PROBE_TIMEOUT ]; do
  if [ ! -e "${SERIAL_PORT}" ]; then
    sleep $PROBE_INTERVAL
    elapsed=$((elapsed + PROBE_INTERVAL))
    continue
  fi
  # if fuser finds a pid, device is in use
  if fuser "${SERIAL_PORT}" >/dev/null 2>&1; then
    sleep $PROBE_INTERVAL
    elapsed=$((elapsed + PROBE_INTERVAL))
    continue
  fi
  # try to set port speed (non-fatal)
  stty -F "${SERIAL_PORT}" ${SERIAL_BAUDRATE} >/dev/null 2>&1 || true
  # consider device ready
  break
done

if [ ! -e "${SERIAL_PORT}" ]; then
  echo "[run_sllidar] device ${SERIAL_PORT} not present after ${PROBE_TIMEOUT}s" >&2
  exit 1
fi

if fuser "${SERIAL_PORT}" >/dev/null 2>&1; then
  echo "[run_sllidar] device ${SERIAL_PORT} is in use" >&2
  exit 1
fi

# Exec the node directly with parameter overrides (more robust than relying on launch file args)
exec ros2 launch sllidar_ros2 sllidar_s1_launch.py
