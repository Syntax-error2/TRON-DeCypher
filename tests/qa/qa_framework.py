import json
import csv
import traceback
import time
from typing import Any, Callable

results = []

def run_qa_test(test_id: str, category: str, feature: str, input_val: Any, expected: Any, test_func: Callable):
    start = time.time()
    try:
        actual = test_func(input_val)
        passed = (actual == expected)
        status = "PASS" if passed else "FAIL"
        err = ""
        acc = 1.0 if passed else 0.0
    except Exception as e:
        actual = str(e)
        status = "FAIL"
        err = traceback.format_exc()
        acc = 0.0
        passed = False
        
    duration = time.time() - start
    
    res = {
        "TEST ID": test_id,
        "CATEGORY": category,
        "FEATURE": feature,
        "INPUT": str(input_val)[:200],
        "EXPECTED": str(expected)[:200],
        "ACTUAL": str(actual)[:200],
        "ACCURACY": acc,
        "STATUS": status,
        "ERROR": err,
        "ROOT CAUSE": "",
        "FIX": "",
        "REGRESSION TEST": ""
    }
    results.append(res)
    if not passed:
        print(f"FAILED: {test_id} - {feature}. Expected {expected} got {actual}")
    return passed

def export_results():
    if not results:
        print("No results to export.")
        return
        
    with open('FINAL_QA_TEST_RESULTS.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    with open('FINAL_QA_TEST_MATRIX.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Generate MD
    total = len(results)
    passed = sum(1 for r in results if r['STATUS'] == 'PASS')
    failed = total - passed
    acc_pct = (passed / total * 100) if total > 0 else 0
    
    md = [
        "# FINAL QA ACCURACY REPORT",
        "",
        "## EXECUTIVE SUMMARY",
        "",
        f"Overall Status: {'PASS' if failed == 0 else 'FAIL'}",
        f"Overall Accuracy: {acc_pct:.1f}%",
        f"Deterministic Test Accuracy: {acc_pct:.1f}%",
        "",
        "## SUMMARY MATRIX",
        "",
        "| Feature | Tests | Passed | Failed | Accuracy | Status |",
        "|---------|-------|--------|--------|----------|--------|"
    ]
    
    cats = {}
    for r in results:
        c = r['CATEGORY']
        if c not in cats:
            cats[c] = {'total': 0, 'passed': 0}
        cats[c]['total'] += 1
        if r['STATUS'] == 'PASS':
            cats[c]['passed'] += 1
            
    for c, stats in cats.items():
        t = stats['total']
        p = stats['passed']
        f_ = t - p
        a = (p / t * 100)
        s = "PASS" if f_ == 0 else "FAIL"
        md.append(f"| {c} | {t} | {p} | {f_} | {a:.1f}% | {s} |")
        
    md.append("")
    md.append("## FAILED TESTS")
    md.append("")
    for r in results:
        if r['STATUS'] != 'PASS':
            md.append(f"### {r['TEST ID']} - {r['FEATURE']}")
            md.append(f"- **Input:** {r['INPUT']}")
            md.append(f"- **Expected:** {r['EXPECTED']}")
            md.append(f"- **Actual:** {r['ACTUAL']}")
            md.append(f"- **Error:** {r['ERROR'].splitlines()[-1] if r['ERROR'] else 'N/A'}")
            md.append("")
            
    with open('FINAL_QA_ACCURACY_REPORT.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
        
    print(f"Exported QA reports. Total: {total}, Passed: {passed}, Failed: {failed}")

