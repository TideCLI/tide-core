#!/usr/bin/env node
/**
 * CLI entry point for Tide coding agent.
 * Uses main.ts with AgentSession and new mode modules.
 */
process.title = "tide";

import { main } from "./main.js";

main(process.argv.slice(2));
