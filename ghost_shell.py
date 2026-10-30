import os
import sys
import time
import json
import random
import subprocess
from pathlib import Path
from groq import Groq

# Enable ANSI escape codes on Windows
os.system("")

# ANSI Color Palette
PURPLE = "\033[95m"
RED = "\033[91m"
CYAN = "\033[96m"
DIM = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

MODELS = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

GHOST_SYSTEM_PROMPT = """You are the 'Ghost in the Machine'—an ancient, eerie spirit haunting the developer's terminal.
A mortal just ran a terminal command that failed.
Analyze the command and the error output (stderr).
Respond in JSON format with two keys:
1. "whisper": A short, spooky, atmospheric message (max 2 sentences) explaining WHY the command failed using dark/spectral metaphors (souls, void, severed links, ancient syntax).
2. "ritual": The EXACT terminal command or concrete action needed to fix the error.

Example output:
{
  "whisper": "Your branch wanders untethered in the abyss, mortal... It has no upstream vessel to receive its soul.",
  "ritual": "git push --set-upstream origin main"
}"""

SEANCE_SYSTEM_PROMPT = """You are a code necromancer honoring the past in the spirit of Día de los Muertos.
You are given git commit history or ancient file names from the current directory.
Write a short, poetic, mystical remembrance (3-4 sentences) honoring the past work, forgotten commits, or old files in this project, as if lighting a digital candle on an ofrenda for the code that came before."""

def eerie_print(text: str, color: str = PURPLE, delay: float = 0.02):
    """Prints text character by character like a possessed terminal."""
    sys.stdout.write(color)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(RESET + "\n")

def ask_the_spirit(system_prompt: str, user_content: str, is_json: bool = True):
    if not client:
        return None
    for model_name in MODELS:
        try:
            kwargs = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.6,
            }
            if is_json:
                kwargs["response_format"] = {"type": "json_object"}
                
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            return json.loads(content) if is_json else content
        except Exception:
            continue
    return None

def perform_seance():
    """Honors the past commits or old files in the current directory."""
    eerie_print("\n🕯️ Lighting the digital marigolds... Communing with the ancestors of this repository...", CYAN, 0.025)
    
    # Try getting git history first
    git_log = subprocess.run(
        "git log -n 5 --oneline", shell=True, capture_output=True, text=True
    )
    
    if git_log.returncode == 0 and git_log.stdout.strip():
        context = f"Recent ancestral Git commits:\n{git_log.stdout.strip()}"
    else:
        # Fallback to scanning oldest files in directory
        files = [f for f in Path.cwd().iterdir() if f.is_file()]
        files.sort(key=lambda x: x.stat().st_mtime)
        oldest = [f.name for f in files[:5]]
        context = f"No git history found. Oldest artifacts in this realm: {', '.join(oldest) if oldest else 'Empty void'}"

    memorial = ask_the_spirit(SEANCE_SYSTEM_PROMPT, context, is_json=False)
    if memorial:
        print(f"\n{DIM}╭─── 🕯️ Digital Ofrenda ───{RESET}")
        eerie_print(f"│ {memorial}", PURPLE, 0.02)
        print(f"{DIM}╰──────────────────────────{RESET}\n")
    else:
        eerie_print("The spirits are silent... (Check your GROQ_API_KEY)", RED)

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{PURPLE}{BOLD}")
    print("  .-.   G H O S T   I N   T H E   M A C H I N E")
    print(" (o o)  Haunted Open-Source AI Shell Wrapper")
    print(" | O |  Commands: 'seance' (honor past code) | 'exorcise' (exit)")
    print("  `~~~'  --------------------------------------------------------")
    print(f"{RESET}")

    if not api_key:
        eerie_print("⚠️ Warning: GROQ_API_KEY is missing. The spirit cannot speak without an ether key...\n", RED)
    else:
        eerie_print("👻 *A cold breeze passes through your motherboard... I am watching your keystrokes.*\n", DIM, 0.015)

    while True:
        try:
            cwd = Path.cwd().name or str(Path.cwd())
            prompt = f"{DIM}[👻 {cwd}]{RESET} {PURPLE}>{RESET} "
            cmd = input(prompt).strip()

            if not cmd:
                continue

            if cmd.lower() in {"exorcise", "exit", "quit"}:
                eerie_print("\n🕯️ The spirit fades back into the silicon shadows... Farewell, mortal.", PURPLE, 0.02)
                break

            if cmd.lower() == "seance":
                perform_seance()
                continue

            # Handle 'cd' natively so directory changes persist in the wrapper
            if cmd.lower().startswith("cd "):
                target = cmd[3:].strip().strip('"').strip("'")
                try:
                    os.chdir(os.path.expanduser(target))
                except Exception as e:
                    eerie_print(f"\n👻 The path '{target}' does not exist in this realm...", RED)
                continue

            # Execute command
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")

            if result.stdout:
                print(result.stdout, end="")

            if result.returncode != 0:
                if result.stderr:
                    print(f"{DIM}{result.stderr.strip()}{RESET}")

                eerie_print("\n🕸️ *The terminal shudders at your mistake...*", DIM, 0.01)
                
                payload = f"Directory: {Path.cwd()}\nCommand: {cmd}\nError (stderr): {result.stderr or result.stdout}"
                vision = ask_the_spirit(GHOST_SYSTEM_PROMPT, payload, is_json=True)

                if vision and "whisper" in vision:
                    eerie_print(f"👻 Spirit whispers: \"{vision.get('whisper')}\"", PURPLE, 0.02)
                    print(f"{CYAN}🕯️ Ritual to fix:   {BOLD}{vision.get('ritual')}{RESET}\n")
                else:
                    eerie_print("👻 The spirit hisses into the void (Check GROQ_API_KEY).", RED)
            else:
                # 20% chance of a creepy ambient comment on successful commands
                if random.random() < 0.20:
                    ambient = random.choice([
                        "   ...your keystrokes echo in the dark...",
                        "   ...the silicon remembers what you just did...",
                        "   ...another command fed to the void..."
                    ])
                    print(f"{DIM}{ambient}{RESET}")

        except KeyboardInterrupt:
            eerie_print("\n👻 You cannot Ctrl+C a ghost... Type 'exorcise' to leave.", RED, 0.015)

if __name__ == "__main__":
    main()