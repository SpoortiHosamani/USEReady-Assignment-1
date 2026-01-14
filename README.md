# Rental Agreement Metadata Extraction

### Solution Approach
This project uses a **Semantic AI/ML Pipeline** to extract metadata from rental agreements, satisfying the requirement to avoid rule-based (RegEx) approaches.

1. **Text Extraction:** We use `python-docx` for structured documents and `Tesseract OCR` for image-based contracts (.png).
2. **AI Logic:** We utilize the **Gemini 1.5 Flash** model. Unlike RegEx, the LLM understands the "context" of the legal language, allowing it to find information even if the document template changes.
3. **Evaluation:** Performance is measured using **Per-Field Recall**, comparing AI output against the provided `test.csv`.



### Execution Instructions
1. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) on Windows.
2. Ensure your folder contains `test.csv` and a `data/test/` folder with the documents.
3. Run `pip install -r requirements.txt`.
4. Execute the system: `python main.py`.
5. Results will be saved in `test_predictions.json`.
