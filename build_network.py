"""
Build a SEMANTIC keyword network from Bible chapter summaries.

Structure:
- SUBJECTS (nouns/actors): God, Abraham, Moses, false prophets, etc.
- Connected to ACTIONS (verbs): gave, warns, leads, teaches
- Connected to OBJECTS/MODIFIERS: glory, covenant, signs
- Finally → CHAPTER (leaf node)

Example: "Warning signs of false prophets everywhere" 
→ false prophets → warning → signs → everywhere → 2 Timothy 3

Uses spaCy NLP for part-of-speech tagging and dependency parsing.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
import spacy

# Load spaCy model
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

# Known Biblical proper nouns (helps with recognition)
BIBLICAL_ENTITIES = {
    'god', 'lord', 'jesus', 'christ', 'spirit', 'father',
    'abraham', 'isaac', 'jacob', 'israel', 'moses', 'aaron', 'david', 
    'solomon', 'elijah', 'elisha', 'isaiah', 'jeremiah', 'ezekiel', 'daniel',
    'peter', 'paul', 'john', 'james', 'matthew', 'mark', 'luke',
    'pharaoh', 'nebuchadnezzar', 'darius', 'cyrus', 'herod', 'pilate',
    'adam', 'eve', 'noah', 'lot', 'sarah', 'rachel', 'ruth', 'esther',
    'samson', 'gideon', 'joshua', 'samuel', 'saul', 'jonathan',
    'judah', 'benjamin', 'joseph', 'ephraim', 'manasseh',
    'moab', 'edom', 'assyria', 'babylon', 'egypt', 'persia', 'rome',
    'jerusalem', 'zion', 'bethlehem', 'nazareth', 'galilee', 'sinai'
}

# Words that should be treated as subject nouns even if not tagged as such
SUBJECT_WORDS = {
    'prophets', 'prophet', 'priests', 'priest', 'king', 'kings', 'queen',
    'people', 'nation', 'nations', 'israelites', 'jews', 'gentiles',
    'disciples', 'apostles', 'believers', 'church', 'servant', 'servants',
    'man', 'men', 'woman', 'women', 'children', 'son', 'sons', 'daughter',
    'angel', 'angels', 'satan', 'devil', 'enemy', 'enemies',
    'wisdom', 'love', 'faith', 'hope', 'grace', 'sin', 'death', 'life'
}


def extract_semantic_chain(summary: str) -> list[dict]:
    """
    Extract a semantic chain from a summary using NLP.
    Returns list of {word, role} where role is 'subject', 'verb', 'object', or 'modifier'
    
    All words are individual nodes - no compound possessives.
    """
    doc = nlp(summary)
    
    chain = []
    seen_words = set()
    
    # Find subjects (nouns that are subjects or known entities)
    subjects = []
    for token in doc:
        word_lower = token.text.lower()
        
        # Check if it's a known Biblical entity
        if word_lower in BIBLICAL_ENTITIES:
            if word_lower not in seen_words:
                subjects.append({'word': word_lower, 'role': 'subject', 'pos': 'PROPN'})
                seen_words.add(word_lower)
            continue
        
        # Check if it's a subject noun
        if token.dep_ in ('nsubj', 'nsubjpass') or word_lower in SUBJECT_WORDS:
            if token.pos_ in ('NOUN', 'PROPN') and word_lower not in seen_words and len(word_lower) > 2:
                subjects.append({'word': word_lower, 'role': 'subject', 'pos': token.pos_})
                seen_words.add(word_lower)
    
    # Find verbs (actions)
    verbs = []
    for token in doc:
        word_lower = token.text.lower()
        if token.pos_ == 'VERB' and word_lower not in seen_words and len(word_lower) > 2:
            # Get lemma for consistency (warns -> warn)
            lemma = token.lemma_.lower()
            if lemma not in seen_words:
                verbs.append({'word': lemma, 'role': 'verb', 'pos': 'VERB'})
                seen_words.add(lemma)
    
    # Find objects and modifiers
    objects = []
    for token in doc:
        word_lower = token.text.lower()
        if word_lower in seen_words:
            continue
        
        # Direct objects
        if token.dep_ in ('dobj', 'pobj', 'attr') and token.pos_ in ('NOUN', 'PROPN'):
            if len(word_lower) > 2:
                objects.append({'word': word_lower, 'role': 'object', 'pos': token.pos_})
                seen_words.add(word_lower)
        # Adjectives and adverbs as modifiers
        elif token.pos_ in ('ADJ', 'ADV') and len(word_lower) > 3:
            objects.append({'word': word_lower, 'role': 'modifier', 'pos': token.pos_})
            seen_words.add(word_lower)
        # Other nouns
        elif token.pos_ in ('NOUN', 'PROPN') and len(word_lower) > 2:
            objects.append({'word': word_lower, 'role': 'object', 'pos': token.pos_})
            seen_words.add(word_lower)
    
    # Build chain: subjects first, then verbs, then objects/modifiers
    chain = subjects + verbs + objects
    
    # If no subjects found, try to use first noun
    if not subjects and chain:
        for item in chain:
            if item['role'] in ('object', 'modifier'):
                item['role'] = 'subject'
                break
    
    return chain


def build_semantic_network(summaries: dict) -> tuple[list, list]:
    """
    Build the semantic network.
    
    Returns (nodes, links) where:
    - nodes: {id, type, role, count, chapters}
    - links: {source, target, weight}
    """
    # Track nodes and their properties
    word_nodes = defaultdict(lambda: {
        'count': 0, 
        'chapters': [], 
        'roles': defaultdict(int)  # Track how often used as each role
    })
    chapter_nodes = {}
    
    # Track links between consecutive elements in chains
    links = defaultdict(int)
    
    print("Analyzing summaries with NLP...")
    
    for i, (chapter, summary) in enumerate(summaries.items()):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(summaries)} chapters...")
        
        # Extract semantic chain
        chain = extract_semantic_chain(summary)
        
        if not chain:
            continue
        
        # Create chapter node with its word chain
        chapter_nodes[chapter] = {
            'id': chapter,
            'type': 'chapter',
            'summary': summary,
            'book': chapter.rsplit(' ', 1)[0],
            'chain': [item['word'] for item in chain]  # Store the actual word sequence
        }
        
        # Track word nodes
        for item in chain:
            word = item['word']
            word_nodes[word]['count'] += 1
            word_nodes[word]['chapters'].append(chapter)
            word_nodes[word]['roles'][item['role']] += 1
        
        # Create sequential links in the chain
        prev = None
        for item in chain:
            word = item['word']
            if prev is not None:
                links[(prev, word)] += 1
            prev = word
        
        # Link last word to chapter
        if chain:
            links[(chain[-1]['word'], chapter)] += 1
    
    print(f"  Processed all {len(summaries)} chapters.")
    
    # Build final node list
    nodes = []
    
    # Determine primary role for each word
    for word, data in word_nodes.items():
        roles = data['roles']
        primary_role = max(roles.keys(), key=lambda r: roles[r]) if roles else 'object'
        
        nodes.append({
            'id': word,
            'type': 'word',
            'role': primary_role,
            'count': data['count'],
            'chapters': data['chapters'][:30]  # Limit for JSON size
        })
    
    # Add chapter nodes
    for chapter, data in chapter_nodes.items():
        nodes.append(data)
    
    # Build links list
    links_list = []
    for (source, target), weight in links.items():
        links_list.append({
            'source': source,
            'target': target,
            'weight': weight
        })
    
    return nodes, links_list


def main():
    input_file = Path("bible_summaries.json")
    output_file = Path("network_data.json")
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        return
    
    print("Loading summaries...")
    with open(input_file, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    
    print(f"Processing {len(summaries)} chapters with semantic analysis...")
    nodes, links = build_semantic_network(summaries)
    
    # Separate by type
    word_nodes = [n for n in nodes if n['type'] == 'word']
    chapter_nodes = [n for n in nodes if n['type'] == 'chapter']
    
    # Count by role
    subjects = [n for n in word_nodes if n.get('role') == 'subject']
    verbs = [n for n in word_nodes if n.get('role') == 'verb']
    objects = [n for n in word_nodes if n.get('role') == 'object']
    modifiers = [n for n in word_nodes if n.get('role') == 'modifier']
    
    print(f"\nNetwork Statistics:")
    print(f"  Subject nodes (actors): {len(subjects)}")
    print(f"  Verb nodes (actions): {len(verbs)}")
    print(f"  Object nodes: {len(objects)}")
    print(f"  Modifier nodes: {len(modifiers)}")
    print(f"  Chapter nodes (leaves): {len(chapter_nodes)}")
    print(f"  Total nodes: {len(nodes)}")
    print(f"  Links: {len(links)}")
    
    # Top subjects
    top_subjects = sorted(subjects, key=lambda x: -x['count'])[:15]
    print(f"\nTop 15 Subjects (actors):")
    for n in top_subjects:
        print(f"  {n['id']}: {n['count']} chapters")
    
    # Top verbs
    top_verbs = sorted(verbs, key=lambda x: -x['count'])[:15]
    print(f"\nTop 15 Verbs (actions):")
    for n in top_verbs:
        print(f"  {n['id']}: {n['count']} chapters")
    
    # Books
    books = sorted(set(n['book'] for n in chapter_nodes))
    
    # Save
    network = {
        'nodes': nodes,
        'links': links,
        'meta': {
            'subjectCount': len(subjects),
            'verbCount': len(verbs),
            'objectCount': len(objects),
            'modifierCount': len(modifiers),
            'chapterCount': len(chapter_nodes),
            'books': books
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(network, f)
    
    print(f"\nNetwork data saved to: {output_file}")


if __name__ == "__main__":
    main()
