from src.parser import parse_invoice_text


def test_parse_invoice_text_basic():
    text = """
    Ma Super Entreprise

    Facture n° 2025-001
    Date : 31/01/2025

    Client : Société Exemple

    Total HT : 100,00 EUR
    TVA : 20,00 EUR
    Total TTC : 120,00 EUR
    """

    invoice = parse_invoice_text(text)

    assert invoice.invoice_number == "2025-001"
    assert invoice.date == "2025-01-31"
    assert invoice.customer == "Société Exemple"
    assert invoice.total_ht == 100.0
    assert invoice.tva == 20.0
    assert invoice.total_ttc == 120.0
