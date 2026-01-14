import os
import json
import pandas as pd
import docx
import pytesseract
from PIL import Image
import google.generativeai as genai
import time

# ==========================================
# 1. WINDOWS PATH FIX (THE ERROR REMOVER)
# ==========================================
# This line tells Python EXACTLY where your OCR engine is.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ==========================================
# 2. CONFIGURATION
# ==========================================
API_KEY = "AIzaSyBJdGp8Ve0AfY52oVMiJ27jWF9jp1iv6Ag"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Paths based on your desktop setup
BASE_PATH = r"C:\Users\spoor\OneDrive\Desktop\AIML project\assignment-1\data"
TEST_DIR = os.path.join(BASE_PATH, "test")
TEST_CSV = os.path.join(BASE_PATH, "test.csv")

# ==========================================
# 3. ROBUST EXTRACTION FUNCTIONS
# ==========================================
def extract_text(file_path):
    """Safe extraction for both formats."""
    try:
        if file_path.lower().endswith('.docx'):
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif file_path.lower().endswith('.png'):
            return pytesseract.image_to_string(Image.open(file_path))
    except Exception as e:
        return f"Error: {str(e)}"
    return ""

def ai_extract_metadata(text):
    """AI/ML logic - satisfies the 'No RegEx' rule."""
    if not text or len(text) < 10:
        return {}
        
    prompt = f"""
    Extract metadata from this agreement. Return ONLY valid JSON.
    Keys: "Agreement Value", "Start Date", "End Date", "Renewal Notice", "Party One", "Party Two"
    Format: Dates as DD.MM.YYYY, Numbers as Integers.
    Text: {text}
    """
    try:
        # We use a retry loop to handle "Rate Limit" errors
        for _ in range(3):
            try:
                response = model.generate_content(prompt)
                clean_json = response.text.replace('```json', '').replace('```', '').strip()
                return json.loads(clean_json)
            except:
                time.sleep(5) # Wait if the API is busy
        return {}
    except:
        return {}

# ==========================================
# 4. EXECUTION & RECALL CALCULATION
# ==========================================


def run_assignment():
    if not os.path.exists(TEST_CSV):
        print(f"FATAL ERROR: Could not find {TEST_CSV}")
        return

    test_df = pd.read_csv(TEST_CSV)
    all_predictions = []
    
    print(f"--- Starting: Processing {len(test_df)} Files ---")
    
    for _, row in test_df.iterrows():
        f_name = str(row['File Name']).strip()
        # Look for the file
        path = os.path.join(TEST_DIR, f"{f_name}.docx")
        if not os.path.exists(path):
            path = os.path.join(TEST_DIR, f"{f_name}.png")

        if os.path.exists(path):
            print(f"-> Processing: {f_name}")
            text = extract_text(path)
            data = ai_extract_metadata(text)
            all_predictions.append(data)
        else:
            print(f"-> Missing File: {f_name}")
            all_predictions.append({})
        
        # Free API limit is 15 RPM. 5 seconds sleep ensures we never hit the error.
        time.sleep(5) 

    # --- FINAL EVALUATION ---
    # Map the Keys (Handles your CSV typos like 'Aggrement')
    mapping = {
        "Agreement Value": "Aggrement Value",
        "Start Date": "Aggrement Start Date",
        "End Date": "Aggrement End Date",
        "Renewal Notice": "Renewal Notice (Days)",
        "Party One": "Party One",
        "Party Two": "Party Two"
    }
    
    print("\n" + "="*35)
    print("FINAL RECALL REPORT")
    print("="*35)
    
    for json_key, csv_key in mapping.items():
        correct = 0
        for i, pred in enumerate(all_predictions):
            actual = str(test_df.iloc[i][csv_key]).strip().lower()
            found = str(pred.get(json_key, "")).strip().lower()
            if actual == found:
                correct += 1
        
        score = correct / len(test_df)
        print(f"{json_key:18}: {score:.2%}")

    # Save output
    with open("final_predictions.json", "w") as f:
        json.dump(all_predictions, f, indent=4)
    print("\nDone! Saved to final_predictions.json")

if __name__ == "__main__":
    run_assignment()