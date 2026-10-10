import requests
import time
import json
import sys

url = "https://truthlens-1-th92.onrender.com/fact-check"

test_cases = [
    # Real-world True news claims
    {"claim": "Donald Trump wants to replace AI with Super Intelligence", "expected": "True"},
    {"claim": "donalad trump says AI to SI", "expected": "True"},
    {"claim": "Trump signed order to use Super Intelligence instead of AI", "expected": "True"},
    {"claim": "Elon Musk renamed SpaceXAI to SpaceXSI", "expected": "True"},
    {"claim": "Apple released Vision Pro headset", "expected": "True"},
    {"claim": "India landed Chandrayaan-3 on the Moon", "expected": "True"},
    {"claim": "OpenAI released GPT-4", "expected": "True"},

    # Real-world False / Negated news claims
    {"claim": "Donald Trump banned all artificial intelligence in the United States", "expected": "False"},
    {"claim": "Humans have landed on Mars", "expected": "False"},
    {"claim": "Apple acquired OpenAI for 500 billion dollars", "expected": "False"},
    {"claim": "NASA confirmed the moon is made of green cheese", "expected": "False"},

    # Questions
    {"claim": "Did Donald Trump rename AI to Super Intelligence?", "expected": "True"},
    {"claim": "Did Apple buy Tesla?", "expected": "False"}
]

print(f"Starting rigorous test suite ({len(test_cases)} cases)...")
print("=" * 70)

results = []

for i, tc in enumerate(test_cases, 1):
    c = tc["claim"]
    exp = tc["expected"]
    try:
        r = requests.post(url, json={"claim": c}, timeout=30)
        data = r.json()
        verdict = data.get("verdict", "Error")
        conf = data.get("confidence", 0)
        sup = data.get("supports", 0)
        con = data.get("contradicts", 0)
        neu = data.get("neutral", 0)
        
        # Consider Uncertain acceptable for claims with no conclusive news
        is_pass = (verdict == exp)
        status = "PASS" if is_pass else "FAIL"
        
        results.append({
            "claim": c,
            "expected": exp,
            "actual": verdict,
            "conf": conf,
            "sup": sup,
            "con": con,
            "neu": neu,
            "pass": is_pass
        })
        
        print(f"[{status}] Case {i:02d}: \"{c}\"")
        print(f"       Expected: {exp} | Actual: {verdict} ({conf}%) [Sup: {sup}, Con: {con}, Neu: {neu}]")
        
        # Print top source if failed
        if not is_pass and data.get("analysis"):
            top = data["analysis"][0]
            print(f"       Top source: [{top.get('label')}] {top.get('title')[:60]}")
            
    except Exception as e:
        print(f"[ERR ] Case {i:02d}: \"{c}\" -> {e}")
        results.append({"claim": c, "expected": exp, "actual": "Error", "pass": False})
        
    time.sleep(1.5)

print("=" * 70)
passed = sum(1 for r in results if r["pass"])
print(f"Test Run Completed: {passed}/{len(results)} passed ({passed/len(results)*100:.1f}%)")
