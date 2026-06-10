# Marlin MCP

An MCP (Model Context Protocol) server that exposes [NemoStation/Marlin-2B](https://huggingface.co/NemoStation/Marlin-2B) — a video language model — as tools for AI assistants. It provides two tools: **describe_video** (caption + scene + events) and **search_video_event** (temporal event grounding).


---

## Architecture

```
Claude / MCP Client
        │
        ▼  port 8006 (HTTP/MCP)
  marlin_mcp.py  ──────────────────► marlin_api.py  (port 8005)
                                           │
                                           ▼
                                     Marlin-2B (GPU)
```

- **marlin_api.py** — FastAPI wrapper that loads the model and exposes `/describe` and `/search` endpoints on port **8005**.
- **marlin_mcp.py** — FastMCP server that wraps those endpoints as MCP tools, served on port **8006**.

---

## Setup

### 1. Update the system

```bash
apt-get update && apt-get upgrade -y
```

### 2. Install Miniconda

```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash ./Miniconda3-latest-Linux-x86_64.sh
```

Restart your shell or run `source ~/.bashrc` after installation.

### 3. Clone the repository

```bash
git clone https://github.com/PromptEngineer48/Marlin-2B-MCP.git
cd Marlin-2B-MCP
```

### 4. Create the conda environment

```bash
conda create -n vlm python=3.13 -y
conda activate vlm
```

### 5. Install MCP and requests

```bash
pip install mcp requests
```

### 6. Install the video model dependencies

```bash
pip install "transformers>=5.7.0" "torch>=2.11.0" torchcodec "qwen-vl-utils>=0.0.14" av pillow
```

### 7. Install torchvision (match your CUDA version)

Find the correct install command for your CUDA version at **https://pytorch.org/** and run it. Example for CUDA 12.4:

```bash
pip install torchvision --index-url https://download.pytorch.org/whl/cu124
```

### 8. Install FastAPI and Uvicorn

```bash
pip install fastapi uvicorn
```

---

## Running on RunPod

Before starting the servers, expose ports **8005** and **8006** in your RunPod pod settings under **HTTP Ports**.

RunPod will give you a public proxy URL for port 8006 in the format:

```
https://<pod-id>-8006.proxy.runpod.net/mcp
```

You will need this URL when configuring your MCP client.

---

## Starting the servers

### Terminal 1 — start the model API (port 8005)

```bash
conda activate vlm
uvicorn marlin_api:app --host 0.0.0.0 --port 8005
```

The first run downloads Marlin-2B (~5 GB). Wait for `Marlin loaded.` before proceeding.

### Terminal 2 — start the MCP server (port 8006)

```bash
conda activate vlm
uvicorn marlin_mcp:app --host 0.0.0.0 --port 8006
```

Your MCP server is now live on **port 8006**.

---

## MCP tools

| Tool | Description |
|---|---|
| `describe_video(video_path)` | Returns `caption`, `scene`, and `events` for a video file |
| `search_video_event(video_path, query)` | Finds the timestamp span of a described event within the video |

---

## Connecting to Hermes

Open your Hermes config file:

```
C:\Users\<your-username>\AppData\Local\hermes\config.yaml
```

Add the `marlin` entry under `mcp_servers`:

```yaml
known_plugin_toolsets:
  mcp_servers:
    claude-code:
      command: claude
      args:
        - mcp
        - serve
      timeout: 300

    marlin:
      url: "https://<your-pod-id>-8006.proxy.runpod.net/mcp"
      timeout: 120
      connect_timeout: 60
```

Replace `<your-pod-id>` with the actual pod ID shown in your RunPod dashboard. The full URL is visible in RunPod under the pod's exposed HTTP ports.

Save the file and restart Hermes — the `marlin` toolset will appear and Marlin's video tools will be available.
