import argparse
from obfuscator import Obfuscator

def main():
    parser = argparse.ArgumentParser(
        description="Obfuscate PII fields in a CSV file using the Obfuscator class."
    )
    parser.add_argument(
        "json_string",
        type=str,
        help="JSON string containing 'file_to_obfuscate' and optional 'pii_fields'.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to save the obfuscated file. Defaults to stdout.",
    )

    args = parser.parse_args()

    try:
        # Create an instance of Obfuscator and process the file
        obfuscator = Obfuscator(args.json_string)
        obfuscated_file = obfuscator.obfuscate()

        # Save to file or print to stdout
        if args.output:
            with open(args.output, "w") as out_file:
                out_file.write(obfuscated_file.getvalue())
            print(f"Obfuscated file saved to {args.output}")
        else:
            print(obfuscated_file.getvalue())

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
