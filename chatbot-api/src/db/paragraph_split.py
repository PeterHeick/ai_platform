import os
import fitz  # PyMuPDF
import re
import spacy

docDir = os.path.join(os.path.dirname(__file__), '../../docs')
print(f"Loading documents from: {docDir}")

# Load SpaCy model
nlp = spacy.load('da_core_news_sm')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

# Function to clean and prepare text
def clean_text(text):
    # Replace hyphen at end of line with nothing to join split words
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    # Normalize whitespace (multiple newlines to double newline)
    text = re.sub(r'\s*\n\s*\n\s*', '\n\n', text.strip())
    return text

# Function to split text into chunks with overlap
def split_text(pdf_path, min_chunk_size=900, max_chunk_size=1100, overlap_size=200):

    text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(text)
    paragraphs = re.split(r'\n\n', text)
    chunks = []
    current_chunk = ""
    current_length = 0

    for para in paragraphs:
        doc = nlp(para)
        sentences = [sent.text.strip() for sent in doc.sents]

        for sent in sentences:
            sent_length = len(sent)
            if current_length + sent_length + 1 <= max_chunk_size:
                current_chunk += " " + sent
                current_length += sent_length + 1
            else:
                if current_length >= min_chunk_size:
                    chunks.append(current_chunk.strip())
                    # Create overlap with last sentences of the current chunk
                    overlap_chunk = " ".join([s for s in sentences if len(current_chunk) - current_chunk.rfind(s) <= overlap_size])
                    current_chunk = overlap_chunk + " " + sent
                    current_length = len(current_chunk)
                else:
                    current_chunk += " " + sent
                    current_length += sent_length + 1

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

if __name__ == "__main__":
  pdf_path = os.path.join(docDir, 'Optagelse af telefonsamtaler.pdf')
  # text = extract_text_from_pdf(pdf_path)
  # cleaned_text = clean_text(text)
  # with open('cleaned_text.txt', 'w') as f:
  #     f.write(cleaned_text)
  chunks = split_text(pdf_path)

  # Print chunks for verification
  with open('chunks.txt', 'w') as f:
      for idx, chunk in enumerate(chunks):
          f.write(f"Chunk {idx + 1}:\n{chunk}\n\n")
