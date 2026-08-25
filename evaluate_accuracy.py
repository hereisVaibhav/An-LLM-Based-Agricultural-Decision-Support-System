import urllib.request
import json
import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# Automated Crop Yield Accuracy Evaluation Pipeline (Parallelized)
# Compares AI-predicted yields against official agricultural statistics
# =============================================================================

# Base benchmark dataset: Ground truth yield configurations
BASE_BENCHMARK = [
    {
        "plant": "Wheat",
        "country": "India",
        "region": "Punjab",
        "temperature": 25,
        "actualYieldPerAcre": 2.0,       # ~50 quintals/hectare
        "source": "India Ministry of Agriculture (2023-24)"
    },
    {
        "plant": "Sugarcane",
        "country": "India",
        "region": "Maharashtra",
        "temperature": 30,
        "actualYieldPerAcre": 33.0,       # ~80 tons/hectare
        "source": "Maharashtra Sugar Commissionerate"
    },
    {
        "plant": "Rice",
        "country": "India",
        "region": "West Bengal",
        "temperature": 28,
        "actualYieldPerAcre": 1.25,       # ~3.1 tons/hectare
        "source": "India Ministry of Agriculture (2023-24)"
    },
    {
        "plant": "Tomato",
        "country": "India",
        "region": "Maharashtra",
        "temperature": 26,
        "actualYieldPerAcre": 12.0,       # Avg industrial tomato yield
        "source": "NHB India Horticulture Statistics"
    },
    {
        "plant": "Corn",
        "country": "USA",
        "region": "Iowa",
        "temperature": 22,
        "actualYieldPerAcre": 4.8,        # ~180 bushels/acre
        "source": "USDA NASS Crop Production Report (2023)"
    },
    {
        "plant": "Soybeans",
        "country": "USA",
        "region": "Illinois",
        "temperature": 21,
        "actualYieldPerAcre": 1.6,        # ~60 bushels/acre
        "source": "USDA NASS Crop Production Report (2023)"
    },
    {
        "plant": "Cotton",
        "country": "USA",
        "region": "Texas",
        "temperature": 29,
        "actualYieldPerAcre": 0.45,       # ~900 lbs/acre lint
        "source": "USDA NASS Cotton Report (2023)"
    }
]

# Generate variations for 5, 10, and 15 acres
BENCHMARK_DATA = []
for crop in BASE_BENCHMARK:
    for size in [5, 10, 15]:
        item = crop.copy()
        item["farmSizeAcres"] = size
        BENCHMARK_DATA.append(item)

NEW_BENCHMARK = [
    {
        "plant": "Wheat",
        "country": "India",
        "region": "Haryana",
        "temperature": 24,
        "actualYieldPerAcre": 1.9,
        "source": "Haryana Department of Agriculture (2023-24)"
    },
    {
        "plant": "Wheat",
        "country": "USA",
        "region": "Kansas",
        "temperature": 20,
        "actualYieldPerAcre": 1.35,
        "source": "USDA NASS Crop Production Report (2023)"
    },
    {
        "plant": "Sugarcane",
        "country": "India",
        "region": "Uttar Pradesh",
        "temperature": 29,
        "actualYieldPerAcre": 31.0,
        "source": "UP Cane Development Department (2023)"
    },
    {
        "plant": "Rice",
        "country": "India",
        "region": "Andhra Pradesh",
        "temperature": 29,
        "actualYieldPerAcre": 1.4,
        "source": "India Ministry of Agriculture (2023-24)"
    },
    {
        "plant": "Tomato",
        "country": "India",
        "region": "Karnataka",
        "temperature": 25,
        "actualYieldPerAcre": 11.0,
        "source": "NHB India Horticulture Statistics"
    },
    {
        "plant": "Potato",
        "country": "India",
        "region": "Uttar Pradesh",
        "temperature": 20,
        "actualYieldPerAcre": 10.5,
        "source": "NHB India Horticulture Statistics"
    },
    {
        "plant": "Potato",
        "country": "USA",
        "region": "Idaho",
        "temperature": 18,
        "actualYieldPerAcre": 18.0,
        "source": "USDA NASS Potato Summary (2023)"
    },
    {
        "plant": "Corn",
        "country": "USA",
        "region": "Nebraska",
        "temperature": 23,
        "actualYieldPerAcre": 4.7,
        "source": "USDA NASS Crop Production Report (2023)"
    },
    {
        "plant": "Corn",
        "country": "Brazil",
        "region": "Mato Grosso",
        "temperature": 30,
        "actualYieldPerAcre": 3.2,
        "source": "CONAB Brazil Crop Bulletin (2023-24)"
    },
    {
        "plant": "Soybeans",
        "country": "USA",
        "region": "Indiana",
        "temperature": 22,
        "actualYieldPerAcre": 1.65,
        "source": "USDA NASS Crop Production Report (2023)"
    },
    {
        "plant": "Soybeans",
        "country": "Brazil",
        "region": "Parana",
        "temperature": 26,
        "actualYieldPerAcre": 1.45,
        "source": "CONAB Brazil Crop Bulletin (2023-24)"
    },
    {
        "plant": "Cotton",
        "country": "USA",
        "region": "Georgia",
        "temperature": 28,
        "actualYieldPerAcre": 0.5,
        "source": "USDA NASS Cotton Report (2023)"
    },
    {
        "plant": "Barley",
        "country": "UK",
        "region": "England",
        "temperature": 18,
        "actualYieldPerAcre": 2.6,
        "source": "UK DEFRA Agriculture Statistics (2023)"
    },
    {
        "plant": "Coffee",
        "country": "Brazil",
        "region": "Minas Gerais",
        "temperature": 24,
        "actualYieldPerAcre": 0.65,
        "source": "CONAB Brazil Coffee Report (2023)"
    },
    {
        "plant": "Tea",
        "country": "India",
        "region": "Assam",
        "temperature": 27,
        "actualYieldPerAcre": 0.85,
        "source": "Tea Board of India Annual Statistics"
    },
    {
        "plant": "Groundnut",
        "country": "India",
        "region": "Gujarat",
        "temperature": 28,
        "actualYieldPerAcre": 0.9,
        "source": "India Ministry of Agriculture (2023-24)"
    },
    {
        "plant": "Onion",
        "country": "India",
        "region": "Nashik",
        "temperature": 27,
        "actualYieldPerAcre": 8.0,
        "source": "NHB India Horticulture Statistics (2023)"
    },
    {
        "plant": "Mustard",
        "country": "India",
        "region": "Rajasthan",
        "temperature": 22,
        "actualYieldPerAcre": 0.55,
        "source": "India Ministry of Agriculture (2023-24)"
    },
    {
        "plant": "Chickpea",
        "country": "India",
        "region": "Madhya Pradesh",
        "temperature": 24,
        "actualYieldPerAcre": 0.45,
        "source": "India Ministry of Agriculture (2023-24)"
    },
    {
        "plant": "Sorghum",
        "country": "India",
        "region": "Maharashtra",
        "temperature": 28,
        "actualYieldPerAcre": 0.4,
        "source": "India Ministry of Agriculture (2023-24)"
    },
    {
        "plant": "Banana",
        "country": "India",
        "region": "Tamil Nadu",
        "temperature": 30,
        "actualYieldPerAcre": 12.0,
        "source": "NHB India Horticulture Statistics (2023)"
    },
    {
        "plant": "Maize",
        "country": "India",
        "region": "Madhya Pradesh",
        "temperature": 27,
        "actualYieldPerAcre": 1.1,
        "source": "India Ministry of Agriculture (2023-24)"
    },
    {
        "plant": "Cassava",
        "country": "Nigeria",
        "region": "Benue State",
        "temperature": 30,
        "actualYieldPerAcre": 3.5,
        "source": "FAO FAOSTAT Nigeria (2023)"
    },
    {
        "plant": "Cocoa",
        "country": "Ghana",
        "region": "Ashanti Region",
        "temperature": 27,
        "actualYieldPerAcre": 0.18,
        "source": "Ghana Cocoa Board (COCOBOD) Annual Report (2023)"
    },
    {
        "plant": "Palm Oil",
        "country": "Malaysia",
        "region": "Sabah",
        "temperature": 29,
        "actualYieldPerAcre": 7.5,
        "source": "MPOB Malaysia Palm Oil Board (2023)"
    },
    {
        "plant": "Rubber",
        "country": "India",
        "region": "Kerala",
        "temperature": 28,
        "actualYieldPerAcre": 0.65,
        "source": "Rubber Board India Annual Statistics (2023)"
    }
]

# Generate variations for 3, 6, and 9 acres for new locations
for crop in NEW_BENCHMARK:
    for size in [3, 6, 9]:
        item = crop.copy()
        item["farmSizeAcres"] = size
        BENCHMARK_DATA.append(item)

# Add one extra case to reach exactly 100
BENCHMARK_DATA.append({
    "plant": "Millet",
    "country": "India",
    "region": "Rajasthan",
    "temperature": 30,
    "actualYieldPerAcre": 0.4,
    "farmSizeAcres": 5,
    "source": "India Ministry of Agriculture (2023-24)"
})

API_URL = "http://localhost:3001/api/yield"
REQUEST_TIMEOUT = 180   # 180 seconds - Gemma 4 reasoning model needs time
MAX_RETRIES = 3
RETRY_DELAY = 3         # seconds between retries

def fetch_prediction(item, attempt=1):
    """Fetch a yield prediction from the backend API with retry logic."""
    data = {
        "plant": item["plant"],
        "farmSizeAcres": item["farmSizeAcres"],
        "temperature": item["temperature"],
        "country": item["country"],
        "region": item["region"]
    }

    req_body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=req_body,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data
    except Exception as e:
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return fetch_prediction(item, attempt + 1)
        return None

def evaluate_item(item):
    """Evaluates a single crop benchmark item."""
    prediction = fetch_prediction(item)
    if not prediction:
        return {"status": "skipped", "item": item, "reason": "No API response"}

    est_tons = prediction.get("yield", {}).get("estimatedTons")
    if est_tons is None:
        return {"status": "skipped", "item": item, "reason": "Could not parse yield"}

    farm_size = item["farmSizeAcres"]
    predicted_per_acre = float(est_tons) / float(farm_size)
    actual_per_acre = item["actualYieldPerAcre"]

    abs_error = abs(predicted_per_acre - actual_per_acre)
    error_pct = (abs_error / actual_per_acre) * 100
    accuracy = max(0.0, 100.0 - error_pct)

    ai_citation = (prediction.get("financials", {}).get("priceSource")
                   or prediction.get("location", {}).get("priceSource")
                   or "N/A")

    result = {
        "Crop": item["plant"],
        "Country": item["country"],
        "Region": item["region"],
        "Farm Size (Acres)": item["farmSizeAcres"],
        "Predicted Yield/Acre (Tons)": round(predicted_per_acre, 3),
        "Actual Yield/Acre (Tons)": round(actual_per_acre, 3),
        "Absolute Error (Tons)": round(abs_error, 3),
        "Error (%)": round(error_pct, 2),
        "Accuracy (%)": round(accuracy, 2),
        "Ground Truth Source": item["source"],
        "AI Price Citation": ai_citation
    }
    return {"status": "ok", "result": result}

def run_evaluation():
    print("=" * 80, flush=True)
    print("  AUTOMATED CROP YIELD ACCURACY EVALUATION PIPELINE (PARALLEL)", flush=True)
    print("  Model: gemma-4-26b-a4b-it  |  Benchmark Cases: {}".format(len(BENCHMARK_DATA)), flush=True)
    print("=" * 80, flush=True)
    print("Evaluating predictions concurrently. Please wait...", flush=True)

    results = []
    skipped = []

    # Run requests concurrently using up to 3 threads to prevent rate limit timeouts
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(evaluate_item, item): item for item in BENCHMARK_DATA}
        
        completed_count = 0
        for future in as_completed(futures):
            item = futures[future]
            label = "{} ({} Ac) in {}".format(item['plant'], item['farmSizeAcres'], item['region'])
            
            try:
                res = future.result()
                if res["status"] == "ok":
                    results.append(res["result"])
                    completed_count += 1
                    print("[{}/{}] OK: {}".format(completed_count, len(BENCHMARK_DATA), label), flush=True)
                else:
                    skipped.append(label)
                    print("[{}/{}] SKIPPED: {} ({})".format(completed_count + len(skipped), len(BENCHMARK_DATA), label, res["reason"]), flush=True)
            except Exception as e:
                skipped.append(label)
                print("Error evaluating {}: {}".format(label, e), flush=True)

    # Sort results for presentation (Crop name, then farm size)
    results.sort(key=lambda x: (x["Crop"], x["Farm Size (Acres)"]))

    # --- Output Report ---
    print("", flush=True)
    print("=" * 80, flush=True)
    print("  EVALUATION RESULTS SUMMARY", flush=True)
    print("=" * 80, flush=True)

    if not results:
        print("No successful predictions were returned. Check backend status.", flush=True)
        return

    # Print Markdown table
    print("| Crop | Region | Size (Ac) | Predicted (T/Ac) | Actual (T/Ac) | Error (T/Ac) | Accuracy | Ground Truth Source |", flush=True)
    print("| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |", flush=True)

    total_acc = 0.0
    for r in results:
        loc = "{}, {}".format(r['Region'], r['Country'])
        print("| {} | {} | {} | {} | {} | {} | {}% | {} |".format(
            r['Crop'], loc,
            r['Farm Size (Acres)'],
            r['Predicted Yield/Acre (Tons)'],
            r['Actual Yield/Acre (Tons)'],
            r['Absolute Error (Tons)'],
            r['Accuracy (%)'],
            r['Ground Truth Source']
        ), flush=True)
        total_acc += r['Accuracy (%)']

    avg_accuracy = total_acc / len(results)

    print("", flush=True)
    print("-" * 80, flush=True)
    print("  Successful tests: {}/{}".format(len(results), len(BENCHMARK_DATA)), flush=True)
    if skipped:
        print("  Skipped: {} ({})".format(len(skipped), ", ".join(skipped)), flush=True)
    print("  AVERAGE MODEL YIELD ACCURACY: {:.2f}%".format(avg_accuracy), flush=True)
    print("-" * 80, flush=True)

    # Save CSV
    csv_file = "accuracy_report.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print("  CSV saved to: {}".format(os.path.abspath(csv_file)), flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    run_evaluation()
