/**
 * OpenRouter login flow.
 *
 * OpenRouter provides access to many models through an OpenAI-compatible API.
 *
 * This is not OAuth - it's a simple API key flow:
 * 1. User creates or copies their API key from OpenRouter
 * 2. User pastes the API key into the CLI
 */

import type { OAuthController } from "./types";

const AUTH_URL = "https://openrouter.ai/docs/api-keys";
const API_KEY_INFO_URL = "https://openrouter.ai/api/v1/key";
const VALIDATION_TIMEOUT_MS = 15_000;

/**
 * Login to OpenRouter.
 *
 * Opens the API key docs, prompts the user to paste their API key,
 * and validates it against OpenRouter's current-key endpoint.
 */
export async function loginOpenRouter(options: OAuthController): Promise<string> {
	if (!options.onPrompt) {
		throw new Error("OpenRouter login requires onPrompt callback");
	}

	options.onAuth?.({
		url: AUTH_URL,
		instructions: "Create or copy your API key",
	});

	const apiKey = await options.onPrompt({
		message: "Paste your OpenRouter API key",
		placeholder: "sk-or-v1-...",
	});

	if (options.signal?.aborted) {
		throw new Error("Login cancelled");
	}

	const trimmed = apiKey.trim();
	if (!trimmed) {
		throw new Error("API key is required");
	}

	options.onProgress?.("Validating API key...");
	await validateOpenRouterApiKey(trimmed, options.signal);
	return trimmed;
}

async function validateOpenRouterApiKey(apiKey: string, signal?: AbortSignal): Promise<void> {
	const timeoutSignal = AbortSignal.timeout(VALIDATION_TIMEOUT_MS);
	const requestSignal = signal ? AbortSignal.any([signal, timeoutSignal]) : timeoutSignal;

	const response = await fetch(API_KEY_INFO_URL, {
		headers: {
			Authorization: `Bearer ${apiKey}`,
		},
		signal: requestSignal,
	});

	if (response.ok) {
		return;
	}

	let details = "";
	try {
		details = (await response.text()).trim();
	} catch {
		// Ignore body parse failures, status code is enough context.
	}

	const message = details
		? `OpenRouter API key validation failed (${response.status}): ${details}`
		: `OpenRouter API key validation failed (${response.status})`;
	throw new Error(message);
}
