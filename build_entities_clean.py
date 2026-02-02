"""
Build clean People/Places lists using comprehensive Bible name lists.
Cross-reference with concordance to only keep indexed words.
"""

import json
from pathlib import Path

# Comprehensive list of Biblical PEOPLE (from Behind the Name and other sources)
BIBLICAL_PEOPLE = """
aaron abel abigail abihu abijah abimelech abinadab abishai abner abraham
absalom achan achish adam adonijah agabus agag agrippa ahab ahaz ahaziah
ahijah ahimaaz ahimelech ahithophel amasa amaziah amnon amon amos ananias
andrew anna annas apollos aquila asa asaph asher athaliah azariah
baanah balaam balak barak barnabas bartholomew baruch barzillai bathsheba
belshazzar benaiah benjamin bezalel bildad bilhah boaz caiaphas cain caleb
chilion cornelius cyrus dan daniel darius david deborah delilah demetrius
dinah doeg dorcas ebed eglon ehud eleazar eli eliab eliezer elihu elijah
elimelech eliphaz elisha elizabeth elkanah enoch enosh ephraim epaphras
epaphroditus esau esther ethan eve ezekiel ezra felix festus gad gamaliel
gedaliah gehazi gershom gideon goliath habakkuk hadassah hagar haggai ham
haman hamor hannah hazael herod hezekiah hilkiah hiram hosea huldah hur
hushai ichabod isaac isaiah ishmael israel issachar ithamar jabin jacob
jael jairus james japheth jason jedidiah jehoahaz jehoiachin jehoiada
jehoiakim jehoram jehoshaphat jehu jephthah jeremiah jeroboam jesse jethro
jezebel joab joanna joash job jochebed joel john jonah jonathan joram
joseph joshua josiah jotham judah judas keturah korah laban lamech lazarus
leah lemuel levi lot luke lydia maacah mahlon malachi manasseh manoah mark
martha mary matthew matthias melchizedek menahem mephibosheth merab meshach
methuselah micah micaiah michal miriam mordecai moses naaman nabal naboth
nadab nahum naomi naphtali nathan nathanael nebuchadnezzar nehemiah nicodemus
noah obadiah obed onesimus orpah othniel paul peninnah peter philemon philip
phinehas pilate potiphar priscilla rachel rahab rebekah rehoboam reuben rhoda
ruth samson samuel sapphira sarah saul seth shadrach shallum shamgar shaphan
sheba shechem shem shimei shiphrah silas simeon simon sisera solomon stephen
tamar terah thomas tiberius timothy titus tobiah tobias uriah uzziah uzziel
vashti zabdi zacchaeus zachariah zadok zebedee zebulun zechariah zedekiah
zephaniah zerubbabel zillah zilpah zimri zipporah
apostle disciple prophet priest pharisee sadducee scribe levite elder
""".lower().split()

# Comprehensive list of Biblical PLACES
BIBLICAL_PLACES = """
accad accho achaia achmetha achshaph achzib adora ai ajalon alexandria
ammon amphipolis anathoth antioch aphek arabia aram ararat armenia aroer
ashdod ashkelon asshur assyria athens azotus baalhazor babylon bashan
beersheba berea bethany bethel bethlehem bethphage bethsaida bithynia
caesarea cana canaan capernaum cappadocia carchemish carmel chaldea
cilicia colossae corinth crete cyprus cyrene damascus dan decapolis
derbe ebal edom edrei eglon egypt ekron elam emmaus endor engedi ephesus
ephraim ethiopia euphrates galatia galilee gath gaza gennesaret gerar gerizim
gethsemane gibeah gibeon gilead gilgal golgotha gomorrah goshen greece
hamath haran hazor hebron hermon horeb iconium idumea israel jabesh
jericho jerusalem jezreel joppa jordan judah judea kadesh kedar kedesh
keilah kidron kirjath lachish lebanon libya lydda lystra machpelah macedonia
mahanaim mamre media megiddo memphis mesopotamia midian miletus mizpah moab
moriah mysia nain naphtali nazareth negev nile nineveh nob ophir paddan
pamphylia paphos paran parthia patmos peniel penuel perga pergamos persia
philadelphia philippi phoenicia phrygia pisgah pisidia pontus ptolemais
puteoli ramah ramoth rephidim rhodes rome salamis salem samaria sardis
sarepta seir seleucia sharon sheba shechem shiloh shinar shunem sidon sinai
smyrna sodom spain succoth susa sychar syria taberah tabor tarsus tekoa
thessalonica thrace thyatira tiberias tigris topheth troas tyre ur zarephath
ziklag zion zoar
temple tabernacle synagogue wilderness mountain river sea desert valley
city gate wall
""".lower().split()

def main():
    # Load concordance
    print("Loading concordance...")
    with open("concordance.json", 'r', encoding='utf-8') as f:
        concordance = json.load(f)
    
    indexed = set(concordance['concordance'].keys())
    print(f"  {len(indexed)} indexed words")
    
    # Filter to only words that are in the concordance
    people = [p for p in BIBLICAL_PEOPLE if p in indexed]
    places = [p for p in BIBLICAL_PLACES if p in indexed]
    
    # Remove duplicates and sort by chapter count
    people = list(set(people))
    places = list(set(places))
    
    # Get counts
    people_counts = {p: len(concordance['concordance'][p]) for p in people}
    places_counts = {p: len(concordance['concordance'][p]) for p in places}
    
    # Sort by count
    people.sort(key=lambda x: -people_counts[x])
    places.sort(key=lambda x: -places_counts[x])
    
    print(f"\nFiltered to indexed words:")
    print(f"  People: {len(people)}")
    print(f"  Places: {len(places)}")
    
    # Save
    output = {
        "people": people,
        "places": places,
        "people_counts": people_counts,
        "places_counts": places_counts
    }
    
    with open("entities.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to entities.json")
    
    print(f"\nTop 30 People:")
    for p in people[:30]:
        print(f"  {p}: {people_counts[p]} chapters")
    
    print(f"\nTop 30 Places:")
    for p in places[:30]:
        print(f"  {p}: {places_counts[p]} chapters")


if __name__ == "__main__":
    main()
