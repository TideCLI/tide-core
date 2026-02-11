#!/usr/bin/env python3
"""
Tide CLI - AI-Powered Coding Assistant for Tide OS
Offline-first CLI using local Ollama models
"""

import argparse
import json
import os
import sys
import subprocess
import textwrap
from pathlib import Path
from typing import Optional
import http.client

# Configuration
DEFAULT_MODEL = "llama3.1:8b"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost")
OLLAMA_PORT = int(os.environ.get("OLLAMA_PORT", "11434"))
CONFIG_DIR = Path.home() / ".tide"
HISTORY_FILE = CONFIG_DIR / "history.json"

# ASCII Art Logo
LOGO = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ████████╗██╗██████╗ ███████╗     ██████╗ ███████╗       ║
║   ╚══██╔══╝██║██╔══██╗██╔════╝    ██╔═══██╗██╔════╝       ║
║      ██║   ██║██║  ██║█████╗      ██║   ██║███████╗       ║
║      ██║   ██║██║  ██║██╔══╝      ██║   ██║╚════██║       ║
║      ██║   ██║██████╔╝███████╗    ╚██████╔╝███████║       ║
║      ╚═╝   ╚═╝╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝       ║
║                                                           ║
║        AI-Powered Linux Distribution - Offline First      ║
╚═══════════════════════════════════════════════════════════╝
"""

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_color(text: str, color: str = Colors.ENDC, end: str = '\n'):
    print(f"{color}{text}{Colors.ENDC}", end=end)

def ensure_config_dir():
    """Ensure config directory exists"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def check_ollama_running() -> bool:
    """Check if Ollama service is running"""
    try:
        conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=5)
        conn.request("GET", "/api/tags")
        response = conn.getresponse()
        conn.close()
        return response.status == 200
    except:
        return False

def get_installed_models() -> list:
    """Get list of installed Ollama models"""
    try:
        conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=10)
        conn.request("GET", "/api/tags")
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        conn.close()
        return data.get("models", [])
    except Exception as e:
        print_color(f"Error fetching models: {e}", Colors.FAIL)
        return []

def pull_model(model: str):
    """Pull a model from Ollama"""
    print_color(f"Pulling model: {model}...", Colors.CYAN)
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        print_color(f"✓ Model {model} pulled successfully!", Colors.GREEN)
    except subprocess.CalledProcessError:
        print_color(f"✗ Failed to pull model {model}", Colors.FAIL)
        sys.exit(1)

def chat_with_model(model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """Send a chat request to Ollama"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=120)
        conn.request("POST", "/api/generate", 
                    body=json.dumps(payload),
                    headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        conn.close()
        return data.get("response", "")
    except Exception as e:
        return f"Error: {e}"

def interactive_chat(model: str):
    """Start an interactive chat session"""
    print(LOGO)
    print_color(f"Model: {model}", Colors.CYAN)
    print_color("Type 'exit', 'quit', or press Ctrl+C to exit\n", Colors.WARNING)
    print_color("Commands:", Colors.HEADER)
    print_color("  /help    - Show this help message", Colors.CYAN)
    print_color("  /models  - List available models", Colors.CYAN)
    print_color("  /clear   - Clear screen", Colors.CYAN)
    print_color("  /code    - Switch to coding mode", Colors.CYAN)
    print_color("  /shell   - Get shell command help", Colors.CYAN)
    print()
    
    system_prompt = None
    conversation_history = []
    
    while True:
        try:
            print_color("You: ", Colors.GREEN, end="")
            user_input = input()
            
            if user_input.lower() in ['exit', 'quit']:
                print_color("\nGoodbye! 👋", Colors.CYAN)
                break
            
            if user_input.startswith('/'):
                handle_command(user_input, model)
                continue
            
            if not user_input.strip():
                continue
            
            # Generate response
            print_color("\nTide: ", Colors.CYAN)
            
            # Build prompt with history
            full_prompt = user_input
            if conversation_history:
                context = "\n\n".join([f"User: {h['user']}\nAssistant: {h['assistant']}" 
                                       for h in conversation_history[-3:]])
                full_prompt = f"Previous conversation:\n{context}\n\nCurrent question: {user_input}"
            
            response = chat_with_model(model, full_prompt, system_prompt)
            print_color(response, Colors.ENDC)
            print()
            
            # Save to history
            conversation_history.append({"user": user_input, "assistant": response})
            
        except KeyboardInterrupt:
            print_color("\n\nGoodbye! 👋", Colors.CYAN)
            break
        except Exception as e:
            print_color(f"Error: {e}", Colors.FAIL)

def handle_command(cmd: str, model: str):
    """Handle special commands"""
    parts = cmd.split()
    command = parts[0].lower()
    
    if command == '/help':
        print_color("""
Tide CLI Commands:
  /help         Show this help message
  /models       List available models
  /clear        Clear the screen
  /code <lang>  Switch to coding mode for specific language
  /shell        Get help with shell commands
  /explain      Explain a command or code
  /write        Generate code for a task
  /fix          Fix provided code
  /review       Review code for improvements
        """, Colors.CYAN)
    
    elif command == '/models':
        models = get_installed_models()
        print_color("\nInstalled Models:", Colors.HEADER)
        for m in models:
            name = m.get('name', 'unknown')
            size = m.get('size', 0) / (1024**3)  # Convert to GB
            print_color(f"  • {name} ({size:.1f} GB)", Colors.CYAN)
        print()
    
    elif command == '/clear':
        os.system('clear' if os.name != 'nt' else 'cls')
    
    elif command == '/code':
        lang = ' '.join(parts[1:]) if len(parts) > 1 else "general"
        print_color(f"Switched to {lang} coding mode. Describe what you want to build:", Colors.CYAN)
    
    elif command == '/shell':
        print_color("Describe what you want to do, and I'll give you the shell command:", Colors.CYAN)
    
    elif command == '/explain':
        print_color("Paste the code/command you want me to explain:", Colors.CYAN)
    
    else:
        print_color(f"Unknown command: {command}. Type /help for available commands.", Colors.WARNING)

def doctor():
    """Run health check"""
    print_color("╔═══════════════════════════════════════╗", Colors.HEADER)
    print_color("║      Tide OS - Health Check           ║", Colors.HEADER)
    print_color("╚═══════════════════════════════════════╝", Colors.HEADER)
    print()
    
    checks = []
    
    # Check Ollama service
    print_color("1. Ollama Service", Colors.HEADER)
    if check_ollama_running():
        print_color("   ✅ Ollama is running", Colors.GREEN)
        checks.append(True)
    else:
        print_color("   ❌ Ollama is NOT running", Colors.FAIL)
        print_color("      Fix: ollama serve", Colors.WARNING)
        checks.append(False)
    
    # Check Ollama API
    print()
    print_color("2. Ollama API", Colors.HEADER)
    if check_ollama_running():
        print_color("   ✅ API responding on port 11434", Colors.GREEN)
        checks.append(True)
    else:
        print_color("   ❌ API not responding", Colors.FAIL)
        checks.append(False)
    
    # Check models
    print()
    print_color("3. Models", Colors.HEADER)
    models = get_installed_models()
    if models:
        print_color("   ✅ Installed models:", Colors.GREEN)
        for m in models:
            name = m.get('name', 'unknown')
            print_color(f"      - {name}", Colors.CYAN)
        checks.append(True)
    else:
        print_color("   ❌ No models installed", Colors.FAIL)
        print_color(f"      Fix: ollama pull {DEFAULT_MODEL}", Colors.WARNING)
        checks.append(False)
    
    # Check Tide config
    print()
    print_color("4. Tide Configuration", Colors.HEADER)
    if CONFIG_DIR.exists():
        print_color(f"   ✅ Config directory: {CONFIG_DIR}", Colors.GREEN)
        checks.append(True)
    else:
        print_color(f"   ⚠️  Config directory will be created: {CONFIG_DIR}", Colors.WARNING)
        checks.append(True)
    
    print()
    print_color("═══════════════════════════════════════", Colors.HEADER)
    if all(checks):
        print_color("✅ All systems operational!", Colors.GREEN)
        print_color("Run 'tide' to start the AI assistant!", Colors.CYAN)
    else:
        print_color("⚠️  Some issues found. Please fix them above.", Colors.WARNING)
    print_color("═══════════════════════════════════════", Colors.HEADER)

def explain_code(code: str, model: str):
    """Explain code using AI"""
    prompt = f"""Please explain this code in detail:

```
{code}
```

Explain:
1. What this code does
2. Key components and logic
3. Any potential issues or improvements
"""
    print_color("Analyzing...", Colors.CYAN)
    response = chat_with_model(model, prompt)
    print_color("\nExplanation:\n", Colors.HEADER)
    print(response)

def generate_shell_command(description: str, model: str):
    """Generate shell command from description"""
    prompt = f"""Convert this task into a shell command:

Task: {description}

Provide only the command, no explanation. If multiple steps are needed, use && to chain them.
"""
    print_color("Generating command...", Colors.CYAN)
    response = chat_with_model(model, prompt).strip()
    print_color("\nSuggested command:\n", Colors.HEADER)
    print_color(f"  {response}", Colors.GREEN)
    print()
    
    confirm = input("Execute? (y/n): ").lower()
    if confirm == 'y':
        print_color("\nExecuting...\n", Colors.CYAN)
        os.system(response)

def write_code(description: str, language: str, model: str):
    """Generate code from description"""
    prompt = f"""Write {language} code for the following:

{description}

Requirements:
- Write clean, well-commented code
- Include error handling where appropriate
- Follow best practices for {language}
- Only output the code, no explanations unless asked
"""
    print_color(f"Generating {language} code...", Colors.CYAN)
    response = chat_with_model(model, prompt)
    print_color(f"\nGenerated {language} code:\n", Colors.HEADER)
    print(response)

def main():
    parser = argparse.ArgumentParser(
        description="Tide CLI - AI-Powered Coding Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
Examples:
  tide                           Start interactive chat
  tide "Hello world"             Send single prompt
  tide --explain "ls -la"        Explain a command
  tide --shell "list files"      Generate shell command
  tide --write "sort algorithm"  Generate code
  tide --doctor                  Run health check
  tide --models                  List available models
  tide --pull llama3.1:8b        Pull a model
        """)
    )
    
    parser.add_argument('prompt', nargs='?', help='Prompt to send to the AI')
    parser.add_argument('--model', '-m', default=DEFAULT_MODEL, help=f'Model to use (default: {DEFAULT_MODEL})')
    parser.add_argument('--explain', '-e', metavar='CODE', help='Explain code or command')
    parser.add_argument('--shell', '-s', metavar='DESCRIPTION', help='Generate shell command from description')
    parser.add_argument('--write', '-w', metavar='DESCRIPTION', help='Generate code from description')
    parser.add_argument('--language', '-l', default='python', help='Programming language for code generation')
    parser.add_argument('--doctor', '-d', action='store_true', help='Run health check')
    parser.add_argument('--models', action='store_true', help='List available models')
    parser.add_argument('--pull', metavar='MODEL', help='Pull a model from Ollama')
    parser.add_argument('--version', '-v', action='version', version='Tide CLI 1.0.0')
    
    args = parser.parse_args()
    
    ensure_config_dir()
    
    # Handle special commands
    if args.doctor:
        doctor()
        return
    
    if args.models:
        models = get_installed_models()
        print_color("Installed Models:", Colors.HEADER)
        for m in models:
            name = m.get('name', 'unknown')
            size = m.get('size', 0) / (1024**3)
            print_color(f"  • {name} ({size:.1f} GB)", Colors.CYAN)
        return
    
    if args.pull:
        pull_model(args.pull)
        return
    
    # Check Ollama is running
    if not check_ollama_running():
        print_color("⚠️  Ollama is not running!", Colors.FAIL)
        print_color("Starting Ollama...", Colors.CYAN)
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        time.sleep(3)
        if not check_ollama_running():
            print_color("Failed to start Ollama. Please start it manually:", Colors.FAIL)
            print_color("  ollama serve", Colors.CYAN)
            sys.exit(1)
    
    # Handle specific modes
    if args.explain:
        explain_code(args.explain, args.model)
        return
    
    if args.shell:
        generate_shell_command(args.shell, args.model)
        return
    
    if args.write:
        write_code(args.write, args.language, args.model)
        return
    
    # Interactive or single prompt mode
    if args.prompt:
        print(LOGO)
        print_color(f"You: {args.prompt}\n", Colors.GREEN)
        print_color("Tide: ", Colors.CYAN)
        response = chat_with_model(args.model, args.prompt)
        print(response)
    else:
        interactive_chat(args.model)

if __name__ == "__main__":
    main()