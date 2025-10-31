# Token counter & cost estimator (independent helper)
# Examples:
#   python scripts\tokens.py --text "hello world"
#   python scripts\tokens.py --file data\sample_kb\01_canonicar_overview.md
#   python scripts\tokens.py --messages-file my_messages.json --assume-output 150 --model gpt-4o-mini

import argparse, json
from app.utils.tokens import TokenAnalyzer


def main():
    p = argparse.ArgumentParser(description="Token counter & cost estimator")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Raw text to analyze")
    g.add_argument("--file", help="Path to a text/markdown file")
    g.add_argument(
        "--messages-file", help="Path to JSON with list of chat messages (role/content)"
    )

    p.add_argument(
        "--model",
        default="gpt-5-nano",
        help="Model id for tokenizer & pricing. Common options: gpt-5-nano, gpt-4o-mini",
    )
    p.add_argument(
        "--assume-output",
        type=int,
        default=200,
        help="Assumed output tokens for cost estimate",
    )

    args = p.parse_args()
    ta = TokenAnalyzer(model=args.model)

    if args.text:
        rep = ta.report_for_text(args.text, assume_output_tokens=args.assume_output)
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        rep = ta.report_for_text(content, assume_output_tokens=args.assume_output)
    else:
        with open(args.messages_file, "r", encoding="utf-8") as f:
            messages = json.load(f)
        rep = ta.report_for_messages(messages, assume_output_tokens=args.assume_output)

    print(f"Model: {rep.model}")
    print(f"Input tokens: {rep.input_tokens}")
    print(f"Assumed output tokens: {rep.assumed_output_tokens}")
    print(f"Estimated cost (USD): {rep.est_cost_usd:.8f}")


if __name__ == "__main__":
    main()
