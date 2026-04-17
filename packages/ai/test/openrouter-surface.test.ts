import { describe, expect, it } from "bun:test";
import { getModel } from "@oh-my-pi/pi-ai/models";
import { getOAuthProviders } from "@oh-my-pi/pi-ai/utils/oauth";

describe("OpenRouter provider surface", () => {
	it("includes OpenRouter in the shared login provider list", () => {
		const providers = getOAuthProviders();
		expect(providers.some(provider => provider.id === "openrouter" && provider.available)).toBe(true);
	});

	it("exposes the MiniMax M2.5 free model through OpenRouter", () => {
		const model = getModel("openrouter", "minimax/minimax-m2.5:free");

		expect(model).toBeDefined();
		expect(model?.provider).toBe("openrouter");
		expect(model?.id).toBe("minimax/minimax-m2.5:free");
		expect(model?.baseUrl).toBe("https://openrouter.ai/api/v1");
	});

	it("exposes Gemma 4 31B free through OpenRouter", () => {
		const model = getModel("openrouter", "google/gemma-4-31b-it:free");

		expect(model).toBeDefined();
		expect(model?.provider).toBe("openrouter");
		expect(model?.id).toBe("google/gemma-4-31b-it:free");
		expect(model?.baseUrl).toBe("https://openrouter.ai/api/v1");
	});
});

describe("GitHub Copilot provider surface", () => {
	it("exposes GPT-5.3-Codex through GitHub Copilot", () => {
		const model = getModel("github-copilot", "gpt-5.3-codex");

		expect(model).toBeDefined();
		expect(model?.provider).toBe("github-copilot");
		expect(model?.id).toBe("gpt-5.3-codex");
		expect(model?.api).toBe("openai-responses");
	});
});
