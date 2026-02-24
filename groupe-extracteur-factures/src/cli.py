import argparse
import json
from pathlib import Path

from .parser import extract_text_from_pdf, parse_invoice_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extracteur de données structurées pour factures PDF."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Chemin vers le fichier PDF de la facture.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Chemin du fichier JSON de sortie (stdout si omis).",
    )

    args = parser.parse_args()

    text = extract_text_from_pdf(args.input)
    invoice = parse_invoice_text(text)
    data = invoice.to_dict()

    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json_str, encoding="utf-8")
        print(f"JSON écrit dans : {output_path}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
