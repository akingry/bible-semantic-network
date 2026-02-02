"""
Manual fixes for weak summaries - hand-written 5-word replacements.
"""

import json

# Manual replacements: chapter -> new summary
FIXES = {
    # Genesis
    "Genesis 1": "God creates heavens, earth, life",
    "Genesis 5": "Adam's genealogy to Noah listed",
    "Genesis 13": "Abram and Lot separate peacefully",
    "Genesis 14": "Abram rescues Lot from kings",
    "Genesis 21": "Isaac born, Hagar sent away",
    "Genesis 22": "Abraham tested, Isaac nearly sacrificed",
    "Genesis 25": "Abraham dies, Esau sells birthright",
    "Genesis 33": "Jacob and Esau reunite peacefully",
    "Genesis 37": "Brothers sell Joseph into slavery",
    "Genesis 39": "Joseph prospers in Potiphar's house",
    "Genesis 47": "Jacob's family settles in Egypt",
    
    # Exodus
    "Exodus 1": "Israelites enslaved, baby boys killed",
    "Exodus 21": "Laws for slaves and injuries",
    "Exodus 24": "Moses receives law on Sinai",
    "Exodus 32": "Israel worships golden calf idol",
    
    # Leviticus
    "Leviticus 5": "Guilt offerings for various sins",
    "Leviticus 15": "Laws about bodily discharges given",
    
    # Numbers
    "Numbers 12": "Miriam punished for opposing Moses",
    "Numbers 21": "Bronze serpent heals snake bites",
    "Numbers 30": "Laws concerning vows and oaths",
    
    # Deuteronomy - check for any
    
    # Joshua
    "Joshua 10": "Sun stands still for Joshua",
    
    # Judges  
    "Judges 4": "Deborah and Barak defeat Sisera",
    "Judges 16": "Samson betrayed by Delilah, dies",
    
    # Ruth
    "Ruth 4": "Boaz marries Ruth, Obed born",
    
    # 1 Samuel
    "1 Samuel 17": "David defeats Goliath with sling",
    
    # 2 Samuel
    "2 Samuel 11": "David commits adultery with Bathsheba",
    
    # 1 Kings
    "1 Kings 18": "Elijah defeats Baal prophets, fire",
    
    # 2 Kings
    "2 Kings 2": "Elijah taken up, Elisha succeeds",
    
    # Psalms - these often have generic summaries
    "Psalms 23": "Lord is my shepherd, provider",
    "Psalms 51": "David repents, asks for mercy",
    "Psalms 119": "Praise for God's law, word",
    
    # Isaiah
    "Isaiah 53": "Suffering servant bears our sins",
    
    # Jeremiah
    "Jeremiah 29": "Letter to exiles, seventy years",
    
    # Daniel
    "Daniel 3": "Three men survive fiery furnace",
    "Daniel 6": "Daniel survives den of lions",
    
    # Jonah
    "Jonah 2": "Jonah prays inside the fish",
    
    # Matthew
    "Matthew 5": "Sermon on Mount, Beatitudes given",
    "Matthew 28": "Jesus rises, Great Commission given",
    
    # Mark
    "Mark 16": "Jesus rises, appears to disciples",
    
    # Luke
    "Luke 2": "Jesus born in Bethlehem, manger",
    "Luke 15": "Lost sheep, coin, prodigal son",
    
    # John
    "John 3": "Nicodemus visits, must be reborn",
    "John 11": "Jesus raises Lazarus from dead",
    
    # Acts
    "Acts 2": "Holy Spirit comes at Pentecost",
    "Acts 9": "Saul converted on Damascus road",
    
    # Romans
    "Romans 8": "No condemnation, Spirit gives life",
    
    # 1 Corinthians
    "1 Corinthians 13": "Love is patient, kind, eternal",
    "1 Corinthians 15": "Resurrection of Christ and believers",
    
    # Galatians
    "Galatians 5": "Fruit of Spirit versus flesh",
    
    # Ephesians
    "Ephesians 6": "Armor of God for battle",
    
    # Philippians
    "Philippians 4": "Rejoice always, peace of God",
    
    # Hebrews
    "Hebrews 11": "Faith heroes throughout Bible history",
    
    # James
    "James 2": "Faith without works is dead",
    
    # Revelation
    "Revelation 21": "New heaven, new earth, Jerusalem",
    "Revelation 22": "River of life, Jesus returns",
}

def main():
    print("Loading summaries...")
    with open("bible_summaries.json") as f:
        summaries = json.load(f)
    
    print(f"Applying {len(FIXES)} manual fixes...\n")
    
    changed = 0
    for chapter, new_summary in FIXES.items():
        if chapter in summaries:
            old = summaries[chapter]
            summaries[chapter] = new_summary
            print(f"{chapter}:")
            print(f"  Old: {old}")
            print(f"  New: {new_summary}\n")
            changed += 1
        else:
            print(f"WARNING: {chapter} not found in summaries")
    
    print(f"\nSaving {changed} changes...")
    with open("bible_summaries.json", 'w', encoding='utf-8') as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    
    print("Done!")
    print("\nNOTE: Run build_network.py to update the network visualization.")


if __name__ == "__main__":
    main()
