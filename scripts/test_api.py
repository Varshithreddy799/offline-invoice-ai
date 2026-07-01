"""Test script for the Offline Invoice AI API."""
import sys
import os
import json
import requests

BASE_URL = "http://localhost:8000"


def test_health():
    print("\n=== Testing Health ===")
    res = requests.get(f"{BASE_URL}/health")
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))
    assert res.status_code == 200
    return res.json()


def test_stats():
    print("\n=== Testing Stats ===")
    res = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))
    assert res.status_code == 200
    return res.json()


def test_upload(file_path):
    print(f"\n=== Testing Upload ({file_path}) ===")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/upload", files={"file": f})
    print(f"Status: {res.status_code}")
    data = res.json()
    print(json.dumps(data, indent=2))
    assert res.status_code == 200
    return data["invoice_id"]


def test_process(invoice_id):
    print(f"\n=== Testing Process (ID: {invoice_id}) ===")
    res = requests.post(f"{BASE_URL}/process/{invoice_id}")
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(json.dumps(res.json(), indent=2))
    else:
        print(f"Error: {res.text}")
    return res.json() if res.status_code == 200 else None


def test_get_invoice(invoice_id):
    print(f"\n=== Testing Get Invoice (ID: {invoice_id}) ===")
    res = requests.get(f"{BASE_URL}/invoice/{invoice_id}")
    print(f"Status: {res.status_code}")
    data = res.json()
    print(json.dumps({k: v for k, v in data.items() if k != "original_ocr"}, indent=2))
    assert res.status_code == 200
    return data


def test_list_invoices():
    print("\n=== Testing List Invoices ===")
    res = requests.get(f"{BASE_URL}/invoices")
    print(f"Status: {res.status_code}")
    data = res.json()
    print(f"Found {len(data)} invoices")
    if data:
        print(json.dumps(data[:2], indent=2))
    assert res.status_code == 200
    return data


def test_search(query):
    print(f"\n=== Testing Search (query: {query}) ===")
    res = requests.get(f"{BASE_URL}/invoices", params={"query": query})
    print(f"Status: {res.status_code}")
    data = res.json()
    print(f"Found {len(data)} invoices matching '{query}'")
    return data


def test_delete(invoice_id):
    print(f"\n=== Testing Delete (ID: {invoice_id}) ===")
    res = requests.delete(f"{BASE_URL}/invoice/{invoice_id}")
    print(f"Status: {res.status_code}")
    print(res.json())
    assert res.status_code == 200
    return res.json()


def test_export(invoice_id):
    print(f"\n=== Testing Export (ID: {invoice_id}) ===")
    for fmt in ["json", "csv", "ocr"]:
        res = requests.get(f"{BASE_URL}/invoice/{invoice_id}/export/{fmt}")
        print(f"  {fmt}: Status {res.status_code}, Length: {len(res.text)} chars")
    return True


def run_all_tests(sample_file=None):
    print("=" * 50)
    print("Offline Invoice AI - API Test Suite")
    print("=" * 50)

    health = test_health()

    test_stats()
    test_list_invoices()

    if sample_file and os.path.exists(sample_file):
        invoice_id = test_upload(sample_file)
        if invoice_id:
            test_process(invoice_id)
            test_get_invoice(invoice_id)
            test_export(invoice_id)
            test_search("TechSupply")
            test_search("INV-2024")
            test_delete(invoice_id)
    else:
        print(f"\n⚠  No sample file provided or found. Use: python {sys.argv[0]} <path_to_image>")
        print("   Upload and process tests skipped.")
        print("   Generate a sample: python scripts/generate_sample_invoice.py")

    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    sample = sys.argv[1] if len(sys.argv) > 1 else None
    if not sample:
        default_sample = os.path.join(
            os.path.dirname(__file__), "..", "uploads", "sample_invoice.png"
        )
        if os.path.exists(default_sample):
            sample = default_sample
    run_all_tests(sample)
