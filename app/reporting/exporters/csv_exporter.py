import csv
from typing import Any


def export_csv(data: dict[str, Any], path: str) -> None:
    # Export findings to main CSV, iocs to a secondary one.
    # For a single file path, we might write a combined or just findings.
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "ID", "Title/Value", "Description"])
        
        for item in data.get("findings", []):
            writer.writerow(["Finding", item.get("id"), item.get("title"), item.get("description")])
            
        for item in data.get("iocs", []):
            writer.writerow(["IOC", item.get("id"), item.get("value"), item.get("ioc_type")])
