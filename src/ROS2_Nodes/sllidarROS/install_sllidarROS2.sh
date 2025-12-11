#!/usr/bin/env bash
set -euo pipefail

# One-click installer builder for sllidar_ros2
# Features:
# - auto-detect ROS 2 distro (supports 'humble' and 'jazzy') or accept argument
# - create workspace (or use provided path)
# - clone or update sllidar_ros2 into src/
# - run rosdep and colcon build

WORKSPACE_DIR="${1:-$(pwd)}"
DISTRO_ARG="${2:-}"

echo "Workspace: ${WORKSPACE_DIR}"

function detect_ros_distro() {
	# Priority: explicit argument, $ROS_DISTRO, common /opt/ros dirs (humble, jazzy)
	if [[ -n "${DISTRO_ARG}" ]]; then
		echo "${DISTRO_ARG}"
		return
	fi
	if [[ -n "${ROS_DISTRO:-}" ]]; then
		echo "${ROS_DISTRO}"
		return
	fi
	for d in humble jazzy; do
		if [[ -f "/opt/ros/${d}/setup.bash" ]]; then
			echo "${d}"
			return
		fi
	done
	# fallback: pick first installed under /opt/ros
	if [[ -d /opt/ros ]]; then
		for p in /opt/ros/*; do
			[[ -d "$p" ]] || continue
			echo "$(basename "$p")"
			return
		done
	fi
	# none found
	echo ""
}

ROS2_DISTRO=$(detect_ros_distro)
if [[ -z "${ROS2_DISTRO}" ]]; then
	echo "Could not detect a ROS 2 installation under /opt/ros/ nor ROS_DISTRO env var." >&2
	echo "Please install ROS2 (humble/jazzy) or pass distro as second arg." >&2
	exit 1
fi

echo "Detected ROS 2 distro: ${ROS2_DISTRO}"

SETUP_SH="/opt/ros/${ROS2_DISTRO}/setup.bash"
if [[ ! -f "${SETUP_SH}" ]]; then
	echo "Expected setup file not found: ${SETUP_SH}" >&2
	exit 1
fi

mkdir -p "${WORKSPACE_DIR}/src"
cd "${WORKSPACE_DIR}"

# Clone or update repository
REPO_URL="https://github.com/Slamtec/sllidar_ros2.git"
TARGET_DIR="${WORKSPACE_DIR}/src/sllidar_ros2"
if [[ -d "${TARGET_DIR}/.git" ]]; then
	echo "sllidar_ros2 already cloned, fetching updates..."
	git -C "${TARGET_DIR}" fetch --all --prune
	git -C "${TARGET_DIR}" pull --ff-only || true
else
	echo "Cloning sllidar_ros2 into src/"
	git clone "${REPO_URL}" "${TARGET_DIR}"
fi

# Source ROS 2 setup
echo "Sourcing ${SETUP_SH}"
# shellcheck disable=SC1090
source "${SETUP_SH}"

# Ensure rosdep is available
if ! command -v rosdep >/dev/null 2>&1; then
	echo "rosdep not found. Please install python3-rosdep and run 'sudo rosdep init && rosdep update' or install via your package manager." >&2
	echo "On Debian/Ubuntu (example): sudo apt update && sudo apt install -y python3-rosdep" >&2
	exit 1
fi

echo "Updating rosdep database (may require network)..."
rosdep update || true

echo "Installing package dependencies from source tree..."
rosdep install --from-paths src --ignore-src -r -y || true

# Ensure colcon exists
if ! command -v colcon >/dev/null 2>&1; then
	echo "colcon not found. Install colcon: sudo apt install -y python3-colcon-common-extensions" >&2
	exit 1
fi

echo "Starting colcon build (this may take several minutes)..."
colcon build --symlink-install --packages-select sllidar_ros2 || {
	echo "colcon build failed. You can inspect logs in ${WORKSPACE_DIR}/log/latest_build" >&2
	exit 1
}

echo "Build finished. To use this workspace run:"
echo "  source ${WORKSPACE_DIR}/install/setup.bash"
echo "Or source the ROS distro first: source ${SETUP_SH}"

# --- 自动写入当前工作目录下的 bashrc（可选） ---
# 在 ${WORKSPACE_DIR}/.bashrc 中添加 source 行，便于在打开新的 shell 时直接使用 workspace
BASHRC_PATH="${WORKSPACE_DIR}/.bashrc"
SOURCE_WORKSPACE_LINE="source ${WORKSPACE_DIR}/install/setup.bash"
SOURCE_ROS_LINE="source ${SETUP_SH}"

echo "Updating ${BASHRC_PATH} to source workspace and ROS setup (idempotent)"
mkdir -p "$(dirname "${BASHRC_PATH}")"
touch "${BASHRC_PATH}"
grep -qxF "${SOURCE_ROS_LINE}" "${BASHRC_PATH}" || printf "\n# Auto-added by install_sllidarROS2.sh\n%s\n" "${SOURCE_ROS_LINE}" >> "${BASHRC_PATH}"
grep -qxF "${SOURCE_WORKSPACE_LINE}" "${BASHRC_PATH}" || printf "%s\n" "${SOURCE_WORKSPACE_LINE}" >> "${BASHRC_PATH}"

echo "Wrote source lines to ${BASHRC_PATH}. To activate in current shell run: source ${BASHRC_PATH}"
# --- 可选：写入用户主目录的 shell rc（不备份原文件），需用户二次确认 ---
USER_RC=""
if [[ -n "${SHELL:-}" ]]; then
	case "$(basename "${SHELL}")" in
		zsh)
			USER_RC="${HOME}/.zshrc"
			;;
		bash)
			USER_RC="${HOME}/.bashrc"
			;;
		*)
			USER_RC="${HOME}/.profile"
			;;
	esac
fi

if [[ -n "${USER_RC}" && -f "${USER_RC}" ]]; then
	echo "About to append ROS2 & workspace source lines to your user rc: ${USER_RC}" >&2
	echo "Warning: this will modify ${USER_RC} without creating a backup." >&2
	read -r -p "Proceed and append to ${USER_RC}? [y/N] " confirm
	if [[ "${confirm,,}" == "y" || "${confirm,,}" == "yes" ]]; then
		touch "${USER_RC}"
		grep -qxF "${SOURCE_ROS_LINE}" "${USER_RC}" || printf "\n# Auto-added by install_sllidarROS2.sh\n%s\n" "${SOURCE_ROS_LINE}" >> "${USER_RC}"
		grep -qxF "${SOURCE_WORKSPACE_LINE}" "${USER_RC}" || printf "%s\n" "${SOURCE_WORKSPACE_LINE}" >> "${USER_RC}"
		echo "Appended lines to ${USER_RC}. To apply now: source ${USER_RC}"
	else
		echo "Skipped modifying ${USER_RC}." >&2
	fi
else
	echo "No user rc file detected (${USER_RC}). Skipping modification of home rc." >&2
fi

exit 0
