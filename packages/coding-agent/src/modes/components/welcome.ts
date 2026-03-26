import { type Component, padding, truncateToWidth, visibleWidth } from "@oh-my-pi/pi-tui";
import { theme } from "../../modes/theme/theme";

export interface RecentSession {
	name: string;
	timeAgo: string;
}

export interface LspServerInfo {
	name: string;
	status: "ready" | "error" | "connecting";
	fileTypes: string[];
}

/**
 * Tide CLI welcome screen with wave-themed logo and two-column layout.
 */
export class WelcomeComponent implements Component {
	constructor(
		private readonly version: string,
		private modelName: string,
		private providerName: string,
		private recentSessions: RecentSession[] = [],
		private lspServers: LspServerInfo[] = [],
	) {}

	invalidate(): void {}

	setModel(modelName: string, providerName: string): void {
		this.modelName = modelName;
		this.providerName = providerName;
	}

	setRecentSessions(sessions: RecentSession[]): void {
		this.recentSessions = sessions;
	}

	setLspServers(servers: LspServerInfo[]): void {
		this.lspServers = servers;
	}

	/** Center text within a given width */
	#centerText(text: string, width: number): string {
		const visLen = visibleWidth(text);
		if (visLen >= width) {
			return truncateToWidth(text, width);
		}
		const leftPad = Math.floor((width - visLen) / 2);
		const rightPad = width - visLen - leftPad;
		return padding(leftPad) + text + padding(rightPad);
	}

	/** Apply Tide CLI ocean gradient (blue→cyan) to a string */
	#tideGradient(line: string): string {
		const colors = [
			"\x1b[38;5;33m", // deep blue
			"\x1b[38;5;39m", // ocean blue
			"\x1b[38;5;45m", // wave blue
			"\x1b[38;5;51m", // bright cyan
			"\x1b[38;5;87m", // light cyan
		];
		const reset = "\x1b[0m";

		let result = "";
		let colorIdx = 0;
		const step = Math.max(1, Math.floor(line.length / colors.length));

		for (let i = 0; i < line.length; i++) {
			if (i > 0 && i % step === 0 && colorIdx < colors.length - 1) {
				colorIdx++;
			}
			const char = line[i];
			if (char !== " ") {
				result += colors[colorIdx] + char + reset;
			} else {
				result += char;
			}
		}
		return result;
	}

	/** Fit string to exact width with ANSI-aware truncation/padding */
	#fitToWidth(str: string, width: number): string {
		const visLen = visibleWidth(str);
		if (visLen > width) {
			const ellipsis = "…";
			const ellipsisWidth = visibleWidth(ellipsis);
			const maxWidth = Math.max(0, width - ellipsisWidth);
			let truncated = "";
			let currentWidth = 0;
			let inEscape = false;
			for (const char of str) {
				if (char === "\x1b") inEscape = true;
				if (inEscape) {
					truncated += char;
					if (char === "m") inEscape = false;
				} else if (currentWidth < maxWidth) {
					truncated += char;
					currentWidth++;
				}
			}
			return `${truncated}${ellipsis}`;
		}
		return str + padding(width - visLen);
	}

	render(termWidth: number): string[] {
		// Box dimensions - responsive with min/max
		const minWidth = 80;
		const maxWidth = 100;
		const boxWidth = Math.max(minWidth, Math.min(termWidth - 2, maxWidth));
		const leftCol = 38;
		const rightCol = boxWidth - leftCol - 3; // 3 = │ + │ + │

		// Tide CLI logo - wide dynamic style with ocean gradient
		// biome-ignore format: preserve ASCII art layout
		const tideLogo = [
			"████████╗██╗██████╗ ███████╗",
			"╚══██╔══╝██║██╔══██╗██╔════╝",
			"   ██║   ██║██║  ██║█████╗  ",
			"   ██║   ██║██║  ██║██╔══╝  ",
			"   ██║   ██║██████╔╝███████╗",
			"   ╚═╝   ╚═╝╚═════╝ ╚══════╝",
			"          CLI               "
		];

		const logoLines = [
			"",
			...tideLogo.map(line => this.#centerText(this.#tideGradient(line), leftCol)),
			"",
			this.#centerText(theme.fg("dim", "～ ～～ 🌊 ～～ ～"), leftCol),
		];

		// Left column - centered content
		const leftLines = [
			"",
			this.#centerText(theme.bold(this.#tideGradient("Welcome to Tide")), leftCol),
			"",
			...logoLines.map(l => this.#centerText(l, leftCol)),
			"",
			this.#centerText(this.#tideGradient(this.modelName), leftCol),
			this.#centerText(theme.fg("dim", this.providerName), leftCol),
		];

		// Right column separator
		const separatorWidth = rightCol - 2; // padding on each side
		const separator = ` ${theme.fg("dim", theme.boxRound.horizontal.repeat(separatorWidth))}`;

		// Recent sessions content
		const sessionLines: string[] = [];
		if (this.recentSessions.length === 0) {
			sessionLines.push(` ${theme.fg("dim", "No recent sessions")}`);
		} else {
			for (const session of this.recentSessions.slice(0, 3)) {
				sessionLines.push(
					` ${this.#tideGradient(theme.md.bullet)} ${this.#tideGradient(session.name)}${theme.fg("dim", ` (${session.timeAgo})`)}`,
				);
			}
		}

		// LSP servers content
		const lspLines: string[] = [];
		if (this.lspServers.length === 0) {
			lspLines.push(` ${theme.fg("dim", "No LSP servers")}`);
		} else {
			for (const server of this.lspServers) {
				const icon =
					server.status === "ready"
						? theme.fg("success", "●")
						: server.status === "connecting"
							? this.#tideGradient("◌")
							: theme.fg("error", "●");
				const exts = server.fileTypes.slice(0, 3).join(" ");
				lspLines.push(` ${icon} ${this.#tideGradient(server.name)} ${theme.fg("dim", exts)}`);
			}
		}

		// Right column
		const rightLines = [
			` ${theme.bold(this.#tideGradient("Tips"))}`,
			` ${this.#tideGradient("?")}${this.#tideGradient(" for keyboard shortcuts")}`,
			` ${this.#tideGradient("/")}${this.#tideGradient(" for commands")}`,
			` ${this.#tideGradient("!")}${this.#tideGradient(" to run bash")}`,
			` ${this.#tideGradient("$")}${this.#tideGradient(" to run python")}`,
			separator,
			` ${theme.bold(this.#tideGradient("LSP Servers"))}`,
			...lspLines,
			separator,
			` ${theme.bold(this.#tideGradient("Recent sessions"))}`,
			...sessionLines,
			"",
		];

		// Border characters (dim)
		const hChar = theme.boxRound.horizontal;
		const h = theme.fg("dim", hChar);
		const v = theme.fg("dim", theme.boxRound.vertical);
		const tl = theme.fg("dim", theme.boxRound.topLeft);
		const tr = theme.fg("dim", theme.boxRound.topRight);
		const bl = theme.fg("dim", theme.boxRound.bottomLeft);
		const br = theme.fg("dim", theme.boxRound.bottomRight);

		const lines: string[] = [];

		// Top border with embedded title
		const title = ` Tide v${this.version} `;
		const titlePrefixRaw = hChar.repeat(3);
		const titleStyled = theme.fg("dim", titlePrefixRaw) + this.#tideGradient(title);
		const titleVisLen = visibleWidth(titlePrefixRaw) + visibleWidth(title);
		const afterTitle = boxWidth - 2 - titleVisLen;
		const afterTitleText = afterTitle > 0 ? theme.fg("dim", hChar.repeat(afterTitle)) : "";
		lines.push(tl + titleStyled + afterTitleText + tr);

		// Content rows
		const maxRows = Math.max(leftLines.length, rightLines.length);
		for (let i = 0; i < maxRows; i++) {
			const left = this.#fitToWidth(leftLines[i] ?? "", leftCol);
			const right = this.#fitToWidth(rightLines[i] ?? "", rightCol);
			lines.push(v + left + v + right + v);
		}

		// Bottom border
		lines.push(bl + h.repeat(leftCol) + theme.fg("dim", theme.boxSharp.teeUp) + h.repeat(rightCol) + br);

		return lines;
	}
}
