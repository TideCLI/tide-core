# Setup

Clean local setup for this repository.

## Prerequisites

- **Bun** `>= 1.3.7` (required by project engines)
- **Node.js** (LTS recommended, needed for npm-based workflows)
- **Git**

## Install prerequisites

### Bun

```bash
curl -fsSL https://bun.sh/install | bash
```

### Node.js

Install from the official site:

- https://nodejs.org/

## 1) Verify tools

```bash
bun --version
node --version
git --version
```

## 2) Clone repository

```bash
git clone <your-repo-url>
cd tide-os
```

(If already cloned, just `cd` into the repo.)

## 3) Install dependencies

```bash
bun install
```

## 4) Optional: link local workspace packages

```bash
bun run install:dev
```

## 5) Start locally

```bash
bun run dev
```

## 6) Validate setup

TypeScript checks:

```bash
bun check:ts
```

Full checks (TypeScript + Rust):

```bash
bun check
```

## Notes

- Main package focus is `packages/coding-agent/`.
- Rust commands require `cargo`/Rust toolchain installed.
