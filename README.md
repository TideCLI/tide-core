<h1 align="center">🌊 Tide OS</h1>

<p align="center">
  <strong>Terminal Intelligence Development Engine</strong><br>
  An AI coding harness for your terminal — available as a CLI or a bootable live Linux ISO.
</p>

<p align="center">
  <a href="https://github.com/SnoozeScript/tide-os/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/SnoozeScript/tide-os/ci.yml?branch=main&style=flat&colorA=0b1a2e&colorB=22d3ee&label=CI" alt="CI"></a>
  <a href="https://github.com/SnoozeScript/tide-os/releases"><img src="https://img.shields.io/github/v/release/SnoozeScript/tide-os?include_prereleases&style=flat&colorA=0b1a2e&colorB=22d3ee&label=release" alt="Release"></a>
  <a href="https://github.com/SnoozeScript/tide-os/blob/main/LICENSE"><img src="https://img.shields.io/github/license/SnoozeScript/tide-os?style=flat&colorA=0b1a2e&colorB=3b82f6" alt="License"></a>
  <a href="https://bun.sh"><img src="https://img.shields.io/badge/runtime-Bun-f472b6?style=flat&colorA=0b1a2e" alt="Bun"></a>
  <a href="https://www.typescriptlang.org"><img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat&colorA=0b1a2e&logo=typescript&logoColor=white" alt="TypeScript"></a>
  <a href="https://www.rust-lang.org"><img src="https://img.shields.io/badge/Rust-DEA584?style=flat&colorA=0b1a2e&logo=rust&logoColor=white" alt="Rust"></a>
</p>

<p align="center">
  <a href="https://snoozescript.github.io/tide-os/"><strong>Website</strong></a> ·
  <a href="https://github.com/SnoozeScript/tide-os/releases">Releases</a> ·
  <a href="https://github.com/SnoozeScript/tide-os/issues">Issues</a>
</p>

---

## What is Tide?

**Tide** (_TIDE — **T**erminal **I**ntelligence **D**evelopment **E**ngine_) is an AI coding harness built for the terminal. It wraps LLMs with the scaffolding that makes them actually useful for real engineering work: tool use, session memory, LSP diagnostics, project awareness, and multi-provider model switching — all from a fast, keyboard-first TUI.

Tide ships two ways:

| | |
|--|--|
| 🖥️ **Tide CLI** | A terminal coding agent you run on your existing machine. `bun run dev` and start working. |
| 💿 **Tide OS (Live ISO)** | A bootable Debian-based live Linux environment with the agent pre-installed. Boot from USB or QEMU, auto-login as the `tide` user, and run `tide`. |

---

## Install

### Option 1 — Clone & run with Bun (recommended)

Requires [Bun](https://bun.sh) `>=1.3.7`:

```bash
git clone https://github.com/SnoozeScript/tide-os
cd tide-os
bun install
bun run dev
```

### Option 2 — Pre-built Linux binary

```bash
curl -fsSL https://github.com/SnoozeScript/tide-os/releases/latest/download/omp-linux-x64 -o omp
chmod +x omp
./omp
```

### Option 3 — Bootable live ISO

Download `tide-os.iso` from the [Releases](https://github.com/SnoozeScript/tide-os/releases) page, then:

```bash
# Boot in QEMU
qemu-system-x86_64 -cdrom tide-os.iso -m 2G -boot d

# Or flash to USB
sudo dd if=tide-os.iso of=/dev/sdX bs=4M status=progress
```

Default login: `tide` / `tide`. Type `tide` to launch the agent.

---

## Features

Tide is a full-featured coding harness. Highlights:

- **Multi-provider** — Claude, ChatGPT, Copilot, Gemini, Cursor, OpenRouter, Perplexity, Mistral, Bedrock, Ollama, and more. Switch models mid-session with `Ctrl+P`.
- **Real tool use** — Bash, git, file edits, LSP diagnostics, Python kernel, web search & fetch. Transparent execution, not a chat box.
- **Session memory** — Every session is saved. Resume with `--continue` or `--resume`.
- **Native TUI** — Custom terminal UI with differential rendering, streaming output, diff viewer, syntax highlighting.
- **LSP-aware** — Format-on-write, diagnostics-on-edit, workspace-wide type checks across 40+ languages.
- **Image generation** — Inline images in Kitty/iTerm2-compatible terminals.
- **Plugins & MCP** — Full Model Context Protocol support, plugin CLI, hot-loadable extensions.
- **Observable** — Built-in `omp stats` dashboard tracks tokens, latency, cost per session and provider.
- **Rust-backed performance** — ~7,500 lines of Rust via N-API for grep, bash, text ops, image decoding, syntax highlighting.

---

## Packages

| Package | Description |
|---|---|
| **[@oh-my-pi/pi-ai](packages/ai)** | Multi-provider LLM client |
| **[@oh-my-pi/pi-agent-core](packages/agent)** | Agent runtime with tool calling and state management |
| **[@oh-my-pi/pi-coding-agent](packages/coding-agent)** | Interactive coding agent CLI (`omp` / `tide`) |
| **[@oh-my-pi/pi-tui](packages/tui)** | Terminal UI library with differential rendering |
| **[@oh-my-pi/pi-natives](packages/natives)** | N-API bindings for grep, shell, image, text, highlighting |
| **[@oh-my-pi/omp-stats](packages/stats)** | Local observability dashboard |

### Rust crates

| Crate | Description |
|---|---|
| **[pi-natives](crates/pi-natives)** | N-API native addon — grep, bash, keys, highlight, image, process tree, and more |
| **[brush-core-vendored](crates/brush-core-vendored)** | Vendored fork of [brush-shell](https://github.com/reubeno/brush) for embedded bash execution |
| **[brush-builtins-vendored](crates/brush-builtins-vendored)** | Vendored bash builtins |

---

## Development

```bash
bun run dev        # run the CLI from source
bun run test       # run all test suites (TS + Rust)
bun run check      # type-check + lint (TS + Rust)
bun run fmt        # format everything
bun run build:native  # build Rust N-API bindings
```

Releasing is automated — bump the version in `package.json`, push to `main`, and the release workflow tags, builds binaries + ISO, and publishes a GitHub Release.

---

## Credits

Tide is a fork of [badlogic/pi-mono](https://github.com/badlogic/pi-mono) by [@mariozechner](https://github.com/mariozechner), with additional work adapted from [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi). The bootable-OS layer, release automation, and rebrand are new in this fork.

---

## License

[MIT](LICENSE) — original work copyright Mario Zechner.
