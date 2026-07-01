from docx import Document
import os, json, re

DOCX_PATH = os.path.join('data', 'CloudSolutionProposal_IT160_sMokhele.docx')
OUT_JSON = os.path.join('data', 'cloud_project.json')
IMG_DIR = os.path.join('static', 'images')

os.makedirs(IMG_DIR, exist_ok=True)

doc = Document(DOCX_PATH)

sections = {}
current = None

for p in doc.paragraphs:
    text = p.text.strip()
    if not text:
        continue
    style = ''
    try:
        style = p.style.name if p.style else ''
    except Exception:
        style = ''
    if style and ('Heading' in style or style.lower().startswith('heading')):
        current = text
        sections[current] = []
    else:
        if current:
            sections.setdefault(current, []).append(text)
        else:
            sections.setdefault('body', []).append(text)

# extract images
images = []
rel_items = list(doc.part._rels.items())
img_count = 0
for rId, rel in rel_items:
    try:
        if 'image' in rel.target_ref:
            img_part = rel.target_part
            data = img_part.blob
            name = os.path.basename(img_part.partname)
            name = f"cloud_doc_image_{img_count}_{name}"
            out_path = os.path.join(IMG_DIR, name)
            with open(out_path, 'wb') as fh:
                fh.write(data)
            images.append(os.path.join('images', name))
            img_count += 1
    except Exception as e:
        # skip problematic relations
        continue

# Heuristic mapping
title = None
if sections:
    # pick the first heading as title if it seems title-like
    for k in sections.keys():
        if len(k.split()) > 1 and len(k) < 80:
            title = k
            break
if not title:
    # fallback to first body paragraph
    title = sections.get('body', [None])[0] or 'Cloud Solution Proposal'

# executive summary
exec_keys = [k for k in sections.keys() if re.search(r'executive|summary|overview|abstract', k, re.I)]
if exec_keys:
    summary = '\n\n'.join(sections[exec_keys[0]])
else:
    summary = '\n\n'.join(sections.get('body', [])[:3])

# focus/objectives
focus_keys = [k for k in sections.keys() if re.search(r'objective|goal|focus|purpose', k, re.I)]
if focus_keys:
    focus = sections[focus_keys[0]]
else:
    # try to extract bullet-like lines from sections
    focus = []
    for k, v in sections.items():
        for line in v:
            if re.match(r'^[\u2022\-\*\d\)]', line) or len(line.split()) < 10:
                focus.append(line)
    if not focus:
        # fallback: split summary into sentences
        sents = re.split(r'(?<=[.!?])\s+', summary)
        focus = sents[:4]

# deliverables
deliver_keys = [k for k in sections.keys() if re.search(r'deliver|deliverable|output|artifact', k, re.I)]
if deliver_keys:
    deliverables = sections[deliver_keys[0]]
else:
    deliverables = []

out = {
    'slug': 'cloud-solution-proposal',
    'title': title,
    'tag': 'Cloud Architecture',
    'summary': summary,
    'focus': focus,
    'attachments': [os.path.basename(DOCX_PATH)],
    'image': images[0] if images else 'images/cloud_solution_proposal.svg',
    'asset_link': None,
    'asset_description': 'Extracted from CloudSolutionProposal_IT160_sMokhele.docx',
    'deliverables': deliverables,
    'sections': sections,
    'images': images
}

with open(OUT_JSON, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=2)

print('WROTE', OUT_JSON)
print('IMAGES', images)
