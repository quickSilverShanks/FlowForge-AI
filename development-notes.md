# Development Notes

The project was built on windows 11 WSL 2.0 with 16GB RAM and 8GB RTX 5060 Laptop GPU.
This file contains development notes for the FlowForge AI project. Anything that went wrong and how it was fixed. This will come in handy when any user is trying to replicate the development environment.



## Docker Compose Issues

### `docker compose build` command returns error:
`Error response from daemon: could not select device driver "nvidia" with capabilities: [[gpu]]`

**Solution:**
First check if wsl has access to GPU and nvidia driver is installed:
```bash
nvidia-smi
```
If nvidia driver is installed within wsl, check for runtime visibility
```bash
docker info | grep -i runtime
```
Its expected to see `Runtimes: nvidia runc`. If only `Runtimes: runc` is visible, toolkit is not configured/installed.
Use below command to see if toolkit is installed. If it gives no output then toolkit is not installed.
```bash
dpkg -l | grep -i nvidia-container
```
If it gives these in the output then toolkit is installed:
`nvidia-container-toolkit`, `libnvidia-container1`, `libnvidia-container-tools`

Below command can also be used. If it gives a version number then toolkit is installed. Otherwise, needs to be installed:
```bash
nvidia-ctk --version
```

If toolkit is not installed, follow below steps to get it installed and configured to be used in docker:
```bash
# STEP 1 — Remove broken NVIDIA repo file (if it was created wrong, like in my case it was created as an html file)
sudo rm /etc/apt/sources.list.d/nvidia-container-toolkit.list

# STEP 2 — Verify your Linux distribution string (used for repo compatibility checks)
. /etc/os-release
echo $ID$VERSION_ID
# Expected output example: ubuntu22.04

# STEP 3 — Add NVIDIA GPG key (modern keyring method, replaces deprecated apt-key)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
| sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
# This stores the trusted key used to verify NVIDIA packages

# STEP 4 — Add NVIDIA container toolkit repository (stable universal repo)
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
| sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
| sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
# This registers the package source with signed-by keyring validation

# STEP 5 — Update apt package index (should complete without <!doctype> errors)
sudo apt update
# Expected: NVIDIA repo fetched successfully, no source list errors

# STEP 6 — Install NVIDIA Container Toolkit (enables Docker GPU runtime)
sudo apt install -y nvidia-container-toolkit
# Installs nvidia-container-runtime and supporting libraries

# STEP 7 — Configure Docker to use NVIDIA runtime + restart service
sudo nvidia-ctk runtime configure --runtime=docker
sudo service docker restart
# Registers NVIDIA runtime inside Docker daemon

# HOW TO CONFIRM FIX — Verify repo file contains valid deb entries (not HTML)
cat /etc/apt/sources.list.d/nvidia-container-toolkit.list
# Expected: Lines starting with "deb [signed-by=...] https://nvidia.github.io/..."

# HOW TO CONFIRM FIX — Verify Docker detects NVIDIA runtime
docker info | grep -i runtime
# Expected output should include: "nvidia" alongside "runc"

# HOW TO CONFIRM FIX — Test GPU access inside a container (did not work for me as i did not have cuda toolkit installed)
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
# Expected: GPU table output showing driver, CUDA, and device utilization
```

