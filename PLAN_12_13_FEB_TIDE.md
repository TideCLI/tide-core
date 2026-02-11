# Tide OS + Tide CLI (2-Day Execution Plan)

## Current status
- [x] `pi-mono` cloned into this repo at `third_party/pi-mono`
- [ ] Tide CLI rebrand build
- [ ] Ollama default model wired (`nemotron-3-nano:latest`)
- [ ] Offline checks + doctor flow
- [ ] Tide OS ISO build
- [ ] Demo evidence package

## Deadline scope (must show 90%)
1. Bootable ISO (live + install)
2. Tide CLI preinstalled (`tide` command)
3. Ollama preinstalled and enabled
4. Model configured for offline (`nemotron-3-nano:latest`)
5. Demo tasks run offline

## Day 1 (Feb 12) — Tide CLI + Offline model integration

### 1) Rebrand coding agent package
Source: `third_party/pi-mono/packages/coding-agent`

Target work tree: `tide-cli/` (copy from source)

Changes:
- package name -> `@tide/tide-cli`
- binary name -> `tide`
- UI name strings -> `Tide`
- config dir default -> `~/.tide/agent` (instead of `~/.pi/agent`)

### 2) Default Ollama provider/model
- Add Tide default model config:
  - provider: `ollama`
  - baseUrl: `http://localhost:11434/v1`
  - api: `openai-completions`
  - model: `nemotron-3-nano:latest`
- Add `tide doctor` check for:
  - Ollama running
  - model exists

### 3) Build and smoke test
- Build CLI
- Verify commands run:
  - `tide`
  - `/model`
  - offline prompt reply

Deliverables by end of Day 1:
- `tide-cli` source
- working local binary/script
- screenshots/logs

## Day 2 (Feb 13) — OS image + ISO + Demo package

### 4) Tide OS Lite base
- Base distro: Ubuntu minimal / Debian live
- Preinstall:
  - `ollama`
  - `tide` CLI
  - first-boot setup service

### 5) First-boot automation
Files to create:
- `packaging/tide-firstboot.sh`
- `packaging/tide-firstboot.service`

Behavior:
- start/enable ollama
- ensure model available (`nemotron-3-nano:latest`)
- run doctor check and write log

### 6) Build ISO
Recommended fast path: Cubic remaster
- inject Tide packages/scripts
- set branding (name/welcome)
- export `tide-os-lite.iso`

### 7) Validation matrix (must pass)
- Boot live ISO
- Install to disk
- Reboot into installed OS
- Run:
  - `tide doctor`
  - one prompt offline
  - one explain command offline
- collect screenshots + terminal logs

Deliverables by end of Day 2:
- `tide-os-lite.iso`
- install and test evidence
- final README + architecture diagram + demo video

## Repo structure (target)

```
.
├── third_party/
│   └── pi-mono/
├── tide-cli/
├── packaging/
│   ├── tide-firstboot.sh
│   ├── tide-firstboot.service
│   └── install_tide.sh
├── iso/
│   └── build-notes.md
└── docs/
    ├── architecture.md
    └── demo-checklist.md
```

## Risk fallback (if ISO packaging slips)
- Deliver VM image + installer script + reproducible build notes
- Keep ISO build as final in-progress step with evidence
