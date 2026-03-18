"""CLI for glitch."""
import sys, json, argparse
from .core import Glitch

def main():
    parser = argparse.ArgumentParser(description="Deja Vu in the Machine — Detecting world model inconsistencies in LLMs. Finding glitches that reveal internal structure.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Glitch()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.detect(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"glitch v0.1.0 — Deja Vu in the Machine — Detecting world model inconsistencies in LLMs. Finding glitches that reveal internal structure.")

if __name__ == "__main__":
    main()
