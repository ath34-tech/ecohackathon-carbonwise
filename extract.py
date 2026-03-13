import docx
import fitz
try:
  doc = docx.Document('prd_eco.docx')
  with open('prd_text.txt', 'w', encoding='utf-8') as f:
    for p in doc.paragraphs:
      f.write(p.text + '\n')
except Exception as e:
  print('Error reading docx:', e)
  try:
    doc = fitz.open('prd_eco.pdf')
    with open('prd_text.txt', 'w', encoding='utf-8') as f:
      for page in doc:
        f.write(page.get_text() + '\n')
  except Exception as e2:
    print('Error reading pdf:', e2)
