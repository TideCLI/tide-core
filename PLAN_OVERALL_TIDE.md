# Tide CLI + Tide OS Lite — Overall Project Plan

## 1) Project Objective
Build a rebranded, offline-first AI terminal experience called **Tide**, based on `pi-mono`'s coding agent core, and ship it inside a lightweight installable OS image (**Tide OS Lite ISO**).

---

## 2) Product Scope

### In scope
- Rebrand CLI from `pi` to `tide`
- Integrate local Ollama provider
- Default offline model: `nemotron-3-nano:latest`
- Add health checks (`tide doctor`)
- Package Tide CLI + Ollama into lightweight OS
- Build bootable/installable ISO
- Provide offline demo evidence

### Out of scope (for this submission)
- Building Linux kernel/OS completely from scratch
- Full custom desktop environment
- Cloud provider integrations

---

## 3) Technical Strategy

### Base code
- Source: `third_party/pi-mono`
- Productized fork: `tide-cli/` from `packages/coding-agent`

### Model backend
- Ollama local endpoint: `http://localhost:11434/v1`
- API mode: OpenAI-compatible (`openai-completions`)
- Default model: `nemotron-3-nano:latest`

### Offline-first behavior
- No cloud API key required for core flow
- Must work without internet after model availability
- Startup checks for Ollama service + model presence

---

## 4) Workstreams

### A) CLI Rebranding Workstream
- Rename package/binary to `tide`
- Rename visible branding (headers, help text, docs)
- Move default config namespace from `.pi` to `.tide` where feasible

### B) Offline Model Integration Workstream
- Add default Ollama provider config
- Add robust fallback/diagnostics for:
  - Ollama not running
  - model missing
  - timeout/errors
- Add `tide doctor` command/check path

### C) OS Integration + ISO Workstream
- Use minimal Debian/Ubuntu base
- Preinstall:
  - Ollama
  - Tide CLI
  - first-boot setup script + systemd service
- Build final ISO with branding

### D) QA & Validation Workstream
- Boot test (live ISO)
- Install test (disk install)
- Reboot test (installed OS)
- Offline test (network disconnected)
- Task validation via Tide commands

### E) Documentation & Demo Workstream
- README with install/use instructions
- Architecture diagram
- Demo script + screenshots/logs
- Contribution attribution for upstream OSS

---

## 5) Deliverables
- `tide-cli/` source fork
- `packaging/` scripts (`install`, `firstboot`, service)
- `tide-os-lite.iso`
- Documentation (`README`, architecture, test evidence)
- Demo recording

---

## 6) 90% Completion Definition
Project is “90% complete” when all of the following are true:

1. ISO boots successfully
2. ISO installs successfully
3. Installed OS reboots cleanly
4. `tide` command available by default
5. Ollama installed and service operational
6. `nemotron-3-nano:latest` configured and usable
7. Offline prompt execution works
8. Offline command explanation works
9. `tide doctor` reports system status correctly
10. Documentation + demo evidence packaged

---

## 7) Remaining 10% (post-demo hardening)
- Performance tuning for low-RAM scenarios
- Better packaging/versioning
- UI polish and branding assets
- Expanded command safety policies
- Additional test coverage and automation
