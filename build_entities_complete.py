"""
Build COMPLETE People/Places lists by:
1. Starting with curated core lists
2. Adding ALL genealogical names from comprehensive sources
3. Cross-referencing with concordance
"""

import json
from pathlib import Path

# Words to EXCLUDE (common nouns, not proper names)
EXCLUDE_WORDS = {
    'lord', 'god', 'spirit', 'father', 'son', 'mother', 'daughter', 'brother',
    'sister', 'king', 'queen', 'prince', 'priest', 'prophet', 'judge', 'elder',
    'servant', 'master', 'slave', 'captain', 'chief', 'ruler', 'governor',
    'ark', 'iron', 'gold', 'silver', 'bronze', 'brass', 'wood', 'stone',
    'promise', 'promised', 'offering', 'sacrifice', 'covenant', 'law',
    'fair', 'mechanic', 'brook', 'reeds', 'wilderness', 'book'
}

# Places that should NOT appear in the People list
PLACES_NOT_PEOPLE = {
    'jerusalem', 'jordan', 'egypt', 'babylon', 'assyria', 'persia', 'greece',
    'rome', 'antioch', 'damascus', 'samaria', 'galilee', 'judea', 'nazareth',
    'bethlehem', 'capernaum', 'jericho', 'hebron', 'bethel', 'shiloh', 'gilgal',
    'sinai', 'horeb', 'carmel', 'tabor', 'hermon', 'lebanon', 'bashan',
    'gilead', 'moab', 'edom', 'ammon', 'midian', 'canaan', 'philistia',
    'phoenicia', 'syria', 'mesopotamia', 'chaldea', 'media', 'elam',
    'arabia', 'ethiopia', 'libya', 'cush', 'sheba', 'ophir', 'tarshish',
    'nineveh', 'tyre', 'sidon', 'gaza', 'ashdod', 'ekron', 'gath', 'ashkelon',
    'sodom', 'gomorrah', 'zoar', 'admah', 'zeboiim', 'shechem', 'dothan',
    'beersheba', 'gerar', 'mamre', 'machpelah', 'peniel', 'mahanaim', 'succoth',
    'zion', 'moriah', 'olivet', 'gethsemane', 'golgotha', 'calvary',
    'corinth', 'ephesus', 'philippi', 'thessalonica', 'colossae', 'galatia',
    'bithynia', 'cappadocia', 'pontus', 'asia', 'macedonia', 'achaia',
    'crete', 'cyprus', 'malta', 'patmos', 'troas', 'miletus', 'caesarea',
    'joppa', 'lydda', 'sharon', 'negev', 'arabah', 'shephelah',
    'euphrates', 'tigris', 'nile', 'arnon', 'jabbok', 'kidron', 'hinnom'
}

# COMPLETE list of Biblical PEOPLE - including genealogies
# Sources: Behind the Name, Bible dictionaries, Genesis 10, 1 Chronicles 1-9
BIBLICAL_PEOPLE = """
aaron abel abagtha abda abdeel abdi abdiel abdon abed abednego abez
abia abiah abialbon abiam abiasaph abiathar abib abida abidah abidan abiel
abiezer abigail abihail abihu abihud abijah abijam abilene abimaaz abimael
abimelech abinadab abinoam abiram abishag abishai abishalom abishua abishur
abital abitub abiud abner abram abraham absalom accad accho achaicus achan
achar achaz achbor achim achish achmetha achor achsa achsah achshaph achzib
adadah adah adaiah adam adar adbeel addan addi addon adem ader adiel adin
adina adino adithaim adlai admah admatha adna adnah adonai adonibezek
adonijah adonikam adoniram adonizedek adoraim adoram adrammelech adramyttium
adria adriel adullam adummim aeneas aenon agabus agag agagite agar agee agrippa
agur ahab aharah aharhel ahasai ahasbai ahasuerus ahava ahaz ahaziah ahban aher
ahi ahiah ahiam ahian ahiezer ahihud ahijah ahikam ahilud ahimaaz ahiman
ahimelech ahimoth ahinadab ahinoam ahio ahira ahiram ahiramites ahisamach
ahishahar ahishar ahithophel ahitub ahlab ahlai ahoah ahohi ahohite aholah
aholiab aholibah aholibamah ahumai ahuzam ahuzzath aiath aijalon ain akan
akkad akkub akrabbim alameth alammelech alamoth alemeth alexander aliah alian
aliah allon almodad almon alpheus alvah alvan amad amal amalek amalekite
amalekites amam amana amariah amasa amasai amashai amashsai amaziah ami aminadab
amittai ammah ammi ammiel ammihud amminadab amminadib ammishaddai ammizabad
ammon ammonite ammonites amnon amok amon amorite amorites amos amoz amplias
ampliatus amram amramite amramites amraphel amzi anab anah anaharath anaiah
anak anakims anamim anammelech anan anani ananiah ananias anath anathoth andrew
andronicus anem aner anetothite aniam anim anna annas annus antioch antipas
antipatris antothijah anub apelles apharsachites apharsathchites apharsites
aphek aphekah aphiah aphik apollonia apollos apollyon appaim apphia aquila
arab arabia arabian arabians arad arah aram aramean arameans aran ararat
araunah arba arbah arbathite arbite archippus archite arcturusard ardon
areli arelites areopagite areopagus aretas argob aridai aridatha ariel arieh
arioch arisai aristarchus aristobulus ark arkite armageddon armoni arnan arni
arod arodi arodites aroer aroerite arpad arpachshad arphaxad artaxerxes artemas
artemis aruboth arumah arvad arvadite arvadites asa asahel asahiah asaiah
asaph asareel asarelah asenath ashan ashbea ashbel ashbelite ashbelites
ashchenaz ashdod ashdodite ashdodites ashdothpisgah asher asherite asherites
ashhur ashima ashkelon ashkenaz ashnah ashpenaz ashriel ashtaroth ashterathite
ashteroth ashtoreth ashur ashurite ashurites ashvath asia asiel asnah asnapper
aspatha asriel asrielites asshurim assir assur assurim assyria assyrian
assyrians asyncritus atad atarah ataroth ater athach athaiah athaliah athenian
athenians athens athlai attai attalia augustus ava aven avim avims avites
avith azal azaliah azaniah azarael azareel azariah azaz azazel azaziah azbuk
azekah azel azem azgad aziel aziza azmaveth azmon aznoth azor azriel azrikam
azubah azur azzah azzan azzur
baal baalah baalbek baalberith baale baalgad baalhamon baalhanan baalhazor
baali baalim baalis baalmeon baalpeor baalperazim baalshalisha baaltamar
baalzebub baalzephon baana baanah baara baaseiah baasha babel babylon babylonian
babylonians baca bachrite bachrites bahurim bajith bakbakkar bakbuk bakbukiah
balaam balac baladan balak bamah bamoth bamothbaal bani barabbas barachel
barachias barak barbarian barhumite bariah barjesus barjona barkos barnabas
barsabas barsabbas bartholomew bartimaeus baruch barzillai bashan bashemath
basmath bathrabbin bathsheba bathshua bavai bazlith bazluth bealiah bealoth
bebai becher bechorath bedad bedan bedaiah beeliada beelzebub beer beerelim
beeri beerlahai beeroth beerothite beerothites beersheba beeshterah behemoth
bel bela belah belaites belial belshazzar belteshazzar ben benaiah benami
beneberak benejaakan benhadad benhail benhanan beninu benjamin benjamite
benjamites beno benoni benzoheth beon beor bera berachah berachiah beraiah
berea bered berechiah beri beriah beriites berith bernice berodach berodachbaladan
berothah berothai berothite besai besodeiah besor betah beten bethany betharabah
betharbel bethaven bethazmaveth bethbaalmeon bethbarah bethbirei bethcar
bethdagon bethel bethelite bethemek bether bethesda bethgader bethgamul
bethhaccerem bethharam bethhogla bethhoglah bethhoron bethjesimoth bethjeshimoth
bethlebaoth bethlehem bethlehemite bethlehemites bethmaacah bethmarcaboth
bethmeon bethnimrah bethpalet bethpazzez bethpeor bethphage bethphelet bethrapha
bethrehob bethsaida bethshan bethshean bethshemesh bethshemite bethtappuah
bethuel bethzur betonim beulah bezai bezaleel bezalel bezek bezer bichri bidkar
bigtha bigthan bigthana bigvai bildad bileam bilgah bilgai bilhah bilhan
bilshan bimhal binea binnui birsha birzaith bishlam bithiah bithron bithynia
bizjothjah biztha blastus boanerges boaz bocheru bochim bohan booz boscath
bosor bozez bozkath bozrah bukki bukkiah bunah bunni buz buzi buzite
cabbon cabul caesar caesarea caiaphas cain cainan calah calamus calcol caleb
calebephratah calneh calno calvary camon cana canaan canaanite canaanites
candace capernaum caphtor caphthorim caphtorim cappadocia carcas carchemish
careah carmel carmelite carmelitess carmi carmites carpus carshena casiphia
casluhim casluhim chaldea chaldean chaldeans chaldees chanaan chedorlaomer
chelal chelluh chelub chelubai chemarims chenaanah chenaniah chenani chephar
chephirah cheran cherethims cherethites cherith cherub cherubim chesalon
chesed chesil chesulloth chezib chidon chileab chilion chilmad chimham chios
chislon chisloth chitlish chloe chorazin christ christian christians chub chun
chushan chuza cilicia cis clauda claudia claudius clement cleopas cleophas
cnidus col colhozeh colosse colossians conaiah conaniah coniah coos corban
core corinth corinthian corinthians cornelius cosam coz cozbi crescens crete
cretes cretians crispus cush cushan cushi cushite cuth cuthah cyprus cyrene
cyrenian cyrenius cyrus
dabria dabbasheth daberath dagon dalmanutha dalmatia dalphon damaris damascene
damascenes damascus dan daniel danite danites dannah dara darda darkon dathan
david debir deborah decapolis dedan dedanim dedanites dekar delaiah delilah
demas demetrius derbe deuel diblaim diblath dibri didymus dimon dimonah dinah
dinhabah dionysius diotrephes dishan dishon dodai dodanim dodavah dodo doeg
dophkah dor dorcas dothan drusilla dumah dura
ebal ebed ebedmelech eben ebenezer eber ebiasaph ebronah ecclesiastes eden
eder edom edomite edomites edrei eglah eglaim eglon egypt egyptian egyptians
ehi ehud eker ekron ekronites el elah elam elamite elamites elasah elath
eldaah eldad elead elealeh eleasah eleazar eled eleph elhanan eli eliab eliada
eliahba eliakim eliam elias eliasaph eliashib eliathah elidad eliel elienai
eliezer elihoenai elihu elijah elika elim elimelech elioenai eliphal eliphaz
elipheleh eliphelet elisha elishah elishama elishaphat elisheba elishua eliud
elizabeth elizaphan elizur elkanah elkosh elkoshite elnaam elnathan eloi
elon elonbethhanan elonites elonim elpaalet elpalet elparan eltekeh eltekon
eltolad elul eluzai elymas elzabad elzaphan emims emmanuel emmaus emmor enam
enan endor eneas eneglaim engedi enoch enos enosh enrimmon enshemesh epaenetus
epaphras epaphroditus epenetus ephah epher ephes ephesians ephesus ephlal
ephod ephraim ephraimite ephraimites ephrain ephratah ephrath ephrathite
ephrathites ephron epicurean epicureans er eran eranites erastus erech eri
erites esaias esau esau esek eshbaal eshban eshcol eshean eshek eshtaol
eshtaulites eshtemoa eshtemoh eshton esli esrom esther etam ethan ethbaal
ethnan ethiopian ethiopians ethnan ethni eubulus eunice euodias euphrates
eutychus eve evi evilmerodach ezbon ezekias ezekiel ezel ezem ezer ezion
eziongaber ezra ezrah ezrahite ezri
fair felix festus fortunatus
gaal gaash gaba gabbai gabbatha gabriel gad gadara gadarenes gadarene gaddi
gaddiel gadi gadite gadites gaham gahar gaius galal galatia galatian galatians
galeed galilee galilean galileans gallim gallio gamaliel gammadims gamul gareb
garmite gashmu gatam gath gathhepher gathrimmon gaza gazer gazez gazite gazzam
geba gebal gebim gedaliah geder gederah gederathite gederite gederoth
gederothaim gedeon gedor gehazi geliloth gemalli gemariah gennesaret genubath
gera gerah gerar gergesenes gerizim gershom gershon gershonite gershonites
gesham geshur geshuri geshurite geshurites gether gethsemane geuel gezer
gezrite giah gibbethon gibea gibeah gibeathite gibeon gibeonite gibeonites
giddal giddalti giddel gideon gideoni gidom gihon gilalai gilboa gilead
gileadite gileadites gilgal giloh gilonite gimzo ginath ginnetho ginnethon
girgashite girgashites girgasite gispa gittahhepher gittaim gittite gittites
gittith gizonite goath gob gog golan golgotha goliath gomer gomorrah goshen
gozan grecia grecians greece greek greeks gur gurhaal
haahashtari habaiah habakkuk habaziniah habor hachaliah hachilah hachmoni
hachmonite hadad hadadrimmon hadar hadarezer hadarimmon hadashah hadassah
hadattah hadid hadlai hadoram hadrach hagab hagaba hagabah hagar hagarene
hagarenes hagarites haggai haggedolim haggeri haggi haggiah haggites haggith
hahiroth hakkatan hakkoz hakupha halah halak halhul hali hallohesh halohesh
ham haman hamath hamathite hamathzobah hamital hammedatha hammoleketh hammon
hammoth hammothdor hamonah hamongog hamor hamoth hamuel hamul hamulites hamutal
hanameel hanamel hanan hananel hanani hananiah hanes haniel hannah hannathon
hanniel hanoch hanochites hanun haphraim hara haradah haran harar hararite
harbona harbonah hareph hareth harhaiah harhur harim hariph harnepher harod
harodite haroeh harorite harosheth harsha harum harumaph haruphite haruz
hasadiah hasenuah hashabiah hashabnah hashabniah hashbadana hashem hashmonah
hashub hashubah hashum hashupha hasrah hassenaah hasshub hasupha hatach hathach
hathath hatipha hatita hattil hattush hauran havilah havothjair hazael hazaiah
hazar hazaraddah hazarenan hazargaddah hazarhatticon hazarmaveth hazarshual
hazarsusah hazarsusim hazelelponi hazeroth hazerim hazeroth haziel hazo hazor
hazzlelponi heber heberites hebrew hebrews hebrewess hebron hebronite hebronites
hegai hege helah helam helbah helbon heldai heleb heled helek helekites helem
heleph helez heli helkai helkath helkathazzurim helon heman hemam hemath hemdan
hen hena henadad henoch hepher hepherites hephzibah heres heresh hereth hermas
hermes hermogenes hermon hermonites herod herodians herodias herodion hesed
heshbon heshmon heth hethlon hezeki hezekiah hezion hezir hezrai hezro hezron
hezronites hiddai hiddekel hiel hierapolis higgaion hilen hilkiah hillel
hinnom hirah hiram hittite hittites hivite hivites hizkiah hizkijah hobab hobah
hod hodaiah hodaviah hodesh hodiah hodijah hoglah hoham holon homam honam hophi
hophni hor horam horeb horem horhaggidgad hori horim horite horites hormah
horonaim horonite hosah hosea hoshaiah hoshama hoshea hotham hothan hothir
hukkok hukok hul huldah humtah hupham huphamites huppah huppim hur hurai huram
huri hushah hushai husham hushatite hushim huz huzzab hymenaeus
ibhar ibnijah ibneiah ibri ibzan ichabod iconium idalah idbash iddo idumaea
idumea igal igdaliah igeal iim ijabarim ijeabarim ijon ikkesh ilai illyricum
imla imlah immanuel immer imna imnah imrah imri india iob iph ira irad iram iri
irijah irnahash iron irpeel irshemesh iru isaac isaiah iscariot ishbah ishbak
ishbibenob ishbosheth ishi ishiah ishijah ishma ishmael ishmaelite ishmael
ishmaelites ishmerai ishod ishpan ishuah ishuai ishui ishmaiah israel israelite
israelites issachar isshiah isshijah italian italy ithamar ithiel ithnan
ithmah ithra ithran ithream ithrite ithrites ittahkazin ittai ivah iye
iyeabarim izehar izhar izharite izharites izliah izrahiah izrahite izri izziah
jaakan jaakobah jaala jaalah jaalam jaanai jaare jaasau jaasiel jaazaniah
jaaziah jaaziel jabbok jabesh jabeshgilead jabez jabin jabneel jabneh jachan
jachin jachinites jacob jada jaddai jaddua jadon jael jagur jah jahath jahaz
jahaza jahaziah jahaziel jahdai jahdiel jahdo jahleel jahleelites jahmai
jahzah jahzeel jahzeelites jahzerah jahziel jailor jair jairite jairus jakan
jakeh jakim jalon jambres james jamin jaminites jamlech janna jannes janoah
janohah janum japheth japhia japhlet japho jarah jareb jared jaresiah jarha
jarib jarmuth jaroah jashen jasher jashob jashobam jashobeam jashub jashubi
jashubilehem jasiel jason jathniel jattir javan jazer jaziz jearim jeatrai
jeatherai jeberechiah jebus jebusite jebusites jecamiah jechiliah jechoniah
jechonias jecoliah jeconiah jedaiah jediael jedidah jedidiah jeduthun jeezer
jeezerites jegar jegarsahadutha jehaleleel jehalelel jehdeiah jehezekel jehiah
jehiel jehieli jehizkiah jehoadah jehoaddan jehoahaz jehoash jehohanan
jehoiachin jehoiada jehoiakim jehoiarib jehonadab jehonathan jehoram jehoshabeath
jehoshaphat jehosheba jehoshua jehoshuah jehovah jehovahjireh jehovahnissi
jehovahshalom jehovahshammah jehovahtsidkenu jehozabad jehozadak jehu jehubah
jehucal jehud jehudi jehudijah jehush jeiel jekabzeel jekameam jekamiah jekuthiel
jemima jemimah jemuel jephthae jephthah jephunneh jerah jerahmeel jerahmeelite
jered jeremiah jeremias jeremoth jeriah jeribai jericho jeriel jerijah jerimoth
jerioth jeroboam jeroham jerubbaal jerubbesheth jeruel jerusalem jesaiah
jesharelah jeshebeab jesher jeshimon jeshishai jeshua jeshuah jeshurun jesiah
jesimiel jesse jesting jesui jesuites jesurun jesus jether jetheth jethro
jetur jeuel jeush jeuz jew jewess jewish jewry jews jezaniah jezebel jezer
jezerites jeziah jeziel jezliah jezoar jezrahiah jezreel jezreelite jezreelitess
jibsam jidlaph jimna jimnah jimnites jiphtah jiphthahel joab joah joahaz
joanna joash joatham job jobab jochebed joda joed joel joelah joezer jogbehah
jogli joha johanan john joiakim joiarib jokdeam jokim jokmeam jokneam jokshan
joktan joktheel jonadab jonah jonan jonas jonathan joppa jorah jorai joram
jordan joribam jorim jorkoam josabad josaphat jose josedech joseph josephus
joses joshah joshaphat joshaviah joshbekashah josheb joshua josiah josias
josibiah josiphiah jotbah jotbathah jotham jozabad jozachar jozadak jubal
jucal juda judaea judah judas jude judea judith julia julius junia junias
jupiter jushab justus
kabzeel kadesh kadeshbarnea kadmiel kadmonites kain kallai kanah kareah karkaa
karkor karnaim kartah kartan kattath kedar kedemah kedemoth kedesh kehelathah
keilah kelaiah kelita kemuel kenan kenath kenaz kenite kenites kenizzite
kenizzites keren kerenhappuch kerioth keros keturah kezia keziah keziz kibroth
kibrothhattaavah kibzaim kidron kinah kir kirharaseth kirhareseth kirharesh
kiriath kiriathaim kiriathbaal kiriathjearim kiriathsanna kiriathsepher kirheres
kirjath kirjathaim kirjatharba kirjatharm kirjatharim kirjathbaal kirjathhuzoth
kirjathjearim kirjathsannah kirjathsepher kish kishi kishion kishon kison
kittim kittites koa kohath kohathite kohathites kolaiah korahite korah korahite
korahites koram kore korhites koz kushaiah
laadah laadan laban lachish ladan lael lahad lahai lahairoi lahmam lahmi
laish lakum lamech lameeh laodicea laodicean laodiceans lapidoth lasea lasha
lasharon lazarus leah leannoth lebanon lebaoth lebonah lecah lehabim lehi
lemuel leshem letushim leummim levi leviathan levite levites levitical libnah
libni libnites libya libyans likhi linus lo lodebar lois lord lot lotan lubim
lucas lucifer lucius lud ludim luhith luke luz lycaonia lycia lydda lydia
lysanias lysias lystra
maacah maachah maachathi maachathite maachathites maadai maadiah maai maaleh
maarath maasai maaseiah maasiai maath maaz maaziah maccabean macedonia
macedonian macedonians machbenah machbenai machi machir machirites machnadebai
machpelah madai madian madmannah madmen madmenah madon magbish magdala magdalene
magdiel magog magor magormissabib magpiash mahalah mahalath mahaleleel mahalel
mahali mahanaim mahanehdan mahanem mahara maharai mahath mahavite mahazioth
maher mahershalalhashbaz mahlah mahli mahlites mahlon mahol makaz makheloth
makkedah maktesh malachi malcam malchiah malchiel malchielites malchijah
malchiram malchishua malchus maleleel mallothi malluch malluchi mammon mamre
manaen manahat manahath manahathites manahethites manasseh manassehite
manassites manoah maoch maon maonites mara marah maralah maranatha marcus
mareshah mark maroth marsena martha mary mas maschil mash mashal masrekah
massa massah matred matri mattan mattanah mattaniah mattatha mattathah mattathias
mattathiah mattenai matthan matthat matthias matthew matthias mattithiah mazzaroth
meah mearah mebunnai mechanic mecherathite medad medan mede medeba medes media
median meeda megiddo megiddon mehetabeel mehetabel mehida mehir meholathite
mehujael mehuman mehunim mehunims mejarkon mekonah melchi melchiah melchisedec
melchishua melchizedek melea melech melicu melita melzar memphis memucan menahem
menan mene menna meonenim meonothai mephaath mephibosheth merab meraioth meraites
merari merarite merarites merathaim mercurius mered meremoth meres meribah
meribaal meribath merib meribbaal merom meronothite meroz mesech mesha meshach
meshech meshelemiah meshezabeel meshezabel meshillemith meshillemoth meshobab
meshullam meshullemeth mesobaite mesopotamia messiah messias metheg methusalah
methusael methuselah meunim mezahab miamin mibhar mibsam mibzar mica micah
micaiah micha michael michah michaiah michal michmash michmas michmethah
michri michtam middin middlemost midian midianite midianitess midianites
migdalgad migdol migron mijamin mikloth mikniah milalai milcah milcom miletum
miletus millo miniamin minni minnith miriam mirma mirmah misgab mishael misham
misheal mishma mishmannah mishraites mispar mispereth misrephoth mithcah
mithnite mithredath mitylene mizar mizpah mizpeh mizpar mizzah mnason moab
moabite moabitess moabites moaldah mochmur moladah molech molid moloch
momordus mordecai moreh moresheth moreshethgath moriah moserah moseroth moses
moza mozah muppim mushi mushite mushites muth muthlabben myra mysia
naam naamah naaman naamath naamathite naamite naarah naarai naaran naarath
naashon nabal nabajoth naboth nachon nachor nadab nadabath nagge nahaliel
nahalol nahallal naham nahamani naharai nahash nahath nahbi nahor nahshon
nahum nain naioth naomi naphtali naphthuhim narcissus nashon nathan nathanael
nathanmelech naum nazarene nazareth nazarite nazirite neah neapolis neariah
nebai nebaioth nebajoth neballat nebat nebo nebuchadnezzar nebuchadrezzar
nebushazban nebuzaradan necho necoda nedabiah neginoth neginah nehelamite
nehemiah nehiloth nehum nehushta nehushtan neiel nekeb nekoda nemuel nemuelites
nepheg nephilim nephish nephishesim nephtali nephtalim nephtoah nephusim ner
nereus nergal nergalsharezer neri neriah nero nethaneel nethaniah nethinim
netophah netophathi netophathite neziah nezib nibhaz nibshan nicanor nicodemus
nicolaitans nicolas nicopolis niger nile nimrah nimrim nimrod nimshi nineveh
ninevite nisan nisroch no noadiah noah nob nobah nobai nod nodab noe nogah
noha non noph nophah nun nymphas
obadiah obal obed obededom obedom obil oboth ocran oded og ohad ohel oholiab
oholibah oholibamah olympas omar omega omer omri on onam onan onesimus onesiphorus
onno ono ophel ophir ophni ophrah oreb oren orion ornain ornan orpah osee
oshea osnapper othni othniel ozem ozias ozni oznites
paarai padan padanaram padon pagiel pahath pai palal palestina palestine pallu
palluite palti paltiel paltite pamphylia pannag paphos paran parah parmashta
parmenas parnach parosh parshandatha parthenians partiuans parvaim pasach
paschal pasdammim paseah pashur patara pathros pathrusim patmos patrobas
pau paul paulus pedaliah pedahel pedahzur pedaiah pekah pekahiah pekod
pelaiah pelaliah pelatiah peleg pelet peleth pelethites peliah pelonite
peniel peninnah pentecost penuel peor perazim perez perezite perezites pereshuzzah
perga pergamos pergamum perida perizzite perizzites persia persian perseus
persis peruda peter pethahiah pethor pethuel peulthai phalec phallu phalti
phaltiel phanuel pharaoh pharaohnecho pharaohnechoh pharaohhophra pharathon
phares pharez pharisee pharisees pharosh pharpar phebe phenice phenicia phichol
philadelphia philemon philetus philip philippi philippians philistia philistim
philistine philistines philologus phinehas phlegon phoenice phoenicia phrygia
phurah phut phuvah phygellus pibeseth pihahiroth pilate pildash pileha pileser
piltai pinon piram pirathon pirathonite pisgah pishon pisidia pison pithom
pithon pochereth potiphar potipherah prisca priscilla prochorus
publius pudens pul punite punites punon pur purah purim put puteoli putiel
quartus
raamah raamiah raama rabbah rabbi rabmag rabsaris rabshakeh rachel radai ragau
raguel raham rahab rahel rakem ram ramah ramath ramathite ramathaim rameses
ramiah ramoth rapha raphah raphu reaiah reba rebekah rechab rechab rechabite
rechabites reelaiah regem regemmelech rehabiah rehob rehoboam rehoboth rehum
rei rekem remaliah remeth remmon remphan rephael rephah rephaiah rephaim
resheph reu reuben reubenite reubenites reuel reumah rezeph rezia rezin rezon
rhegium rhesa rhoda rhode rhodes ribai rimmon rinnah riphath rizia rizpah
roggelim rohgah romamti roman romans rome romph rosh rufus ruhamah ruth
sabachthani sabaoth sabeans sabtah sabtecha sacar sadducee sadducees sadoc
salah salamis salathiel salcah salem salim sallai sallu salma salmon salome
salu samaria samaritan samaritans samlah samos samothracia samson samuel sanballat
saph saphir sapphira sarah sarai saraph sargon sarsechim saruch satan saul
sceva scribes scythian seba secacah sechu secundus segub seir sela selah seled
seleucid sem semachiah semei semein senaah seneh senir sennacherib senuah
seorim sephar sepharad sepharvaim serah seraiah seraphim sered sergius serug
seth sethur shaalabbin shaaraim shaashgaz shabbethai shachia shadrach shage
shahar shaharaim shahazimah shalim shallum shallun shalmai shalman shalmaneser
shama shamariah shamed shamer shamgar shamhuth shamir shamma shammah shammai
shammoth shammua shammuah shamsherai shapham shaphan shaphat shaphir sharai
sharaim sharar sharezer sharon sharonite sharuhen shashai shashak shaul
shaulites shaveh shavsha sheal shealtiel sheariah shearjashub sheba shebah
shebaniah shebat sheber shebna shebuel shechaniah shechem shechemite shechemites
shedeur shehariah shelah shelanites shelemiah sheleph shelesh shelomi shelomith
shelomoth shelumiel shem shema shemaiah shemariah shemeber shemer shemida
shemidah shemidaites sheminith shemiramoth shemuel shen shenazar shenazzar
shenir shepham shephathiah shephatiah shephi shepho shephuphan sherah sherezer
sheresh sheshach sheshai sheshan sheshbazzar sheth shethar shetharboznai sheva
shibah shibboleth shicron shigionoth shihon shihor shihorlibnath shilhi shilhim
shillem shillemites shiloah shiloh shiloni shilonite shilonites shilshah shimea
shimeah shimeam shimeath shimeathite shimeathites shimei shimeon shimhi shimi
shimites shimma shimon shimrath shimri shimrith shimrom shimron shimronites
shimronmeron shimshai shinab shinar shiphi shiphite shiphmite shiphrah shiphtan
shisha shishak shitrai shittim shiza shoa shobab shobach shobai shobal shobek
shochoh shoham shomer shophan shophach shua shuah shual shubael shuham shuhamites
shuhite shulamite shulamith shumathites shunem shunemmite shunite shupham
shuphamites shuppim shur shushan shuthalhites shuthelah sia siaha sibbecai
sibbechai sibboleth sibmah sichem siddim sidon sidonian sidonians sihon sihor
silas silla siloah siloam silvanus simeon simeonite simeonites simon simri
sinai sion siph siphmoth sippai sirah sirion sisera sisinnes sitnah sivan
smyrna so socoh sochoth soco sodi sodom sodomite sodomites solomon sopater
sophereth sosipater sosthenes sotai spain stachys stephanas stephen stoics
suah succoth succothbenoth sukkiim sukkites sumer suph sur susanchites susanna
susi sychem syene synagogue syntyche syracuse syria syrians syrophoenician
syrophenician syrtis
taanach taanathshiloh tabbaoth tabbath tabeal tabeel taberah tabering tabitha
tabor tabrimon tadmor tahan tahanites tahapanes tahath tahpanes tahpanhes
tahrea tirhakah talmud talmai talmon tamah tamar tammuz tanach tanhumeth
taphath tappuah tarah taralah tarea tarshish tarsus tartak tartan tattenai tebah
tebaliah tebeth tehaphnehes tehinnah tekel tekoa tekoite tel telaim telassar
telem telharsa telharesha telmelah tema temah teman temani temanite temeni
terah teraphim teresh tertius tertullus thaddaeus thahash thamah thamar thara
tharshish thebes thelasar theophilus thessalonica thessalonians theudas thomas
thummim thyatira tiberias tiberius tibhath tibni tidal tiglath tiglathpileser
tikvah tikvath tildad tilon timaeus timna timnah timnath timnatheres timnathheres
timnathserah timnite timon timotheus timothy tiphsah tirhakah tirhana tirhanah
tiria tirshatha tirzah tishbite titus tizite toah tob tobadonijah tobiah
tobijah tochen togarmah tohu toi tola tolaites tolad tophel tophet topheth
tou trachonitis troas trogyllium trophimus tryphena tryphon tryphosa tubal
tubalcain tychicus tyrannus tyre tyrian tyrians tyrus
ucal uel ulai ulam ulla unni uphaz ur urbane uri uriah uriel urim urijah
uthai uz uzai uzal uzzah uzza uzzah uzzen uzzensherah uzzi uzzia uzziah uzziel
uzzielites
vajezatha vaniah vashni vashti vophsi
zaanaim zaanan zaavan zabad zabadaias zabadeans zabbai zabbud zabdi zabdiel
zabud zaccai zacchaeus zacchur zaccur zachariah zacharias zadok zaham zair
zalaph zalmon zalmonah zalmunna zamzummims zanoah zaphenath zaphenathpaneah
zaphon zarah zareah zared zarephath zaretan zareth zarethshahar zarhites zarthan
zatthu zattu zaza zebadiah zebah zebedee zebina zeboiim zeboim zebudah zebul
zebulonite zebulonites zebulun zechariah zedad zedekiah zeeb zelah zelek zelophehad
zelotes zelzah zemaraim zemarite zemira zenan zenas zephaniah zephath zephathah
zephi zephon zephonites zer zerah zerahiah zerahites zered zereda zeredah
zeredathah zererath zeresh zereth zerethahar zeri zeror zeruah zerubbabel zeruiah
zetham zethan zethar zia ziba zibeon zibia zibiah zichri ziddim zidkijah zidon
zidonians zif ziha ziklag zillah zillethai zilpah zilthai zimmah zimran zimri
zina zion ziph ziphah ziphims ziphion ziphites ziphron zippor zipporah zithri
ziv ziza zizah zobah zobebah zohar zoheleth zoheth zophah zophai zophar zophim
zorah zorathites zoreah zorites zorobabel zuar zuph zur zuriel zurishaddai
zuzims
""".lower().split()

# COMPLETE list of Biblical PLACES
BIBLICAL_PLACES = """
abana abarim abel abelacacia abelbethmaacah abelcheramim abelmaim abelmeholah
abelmizraim abelshittim abilene accad accho achaia achmetha achor achshaph
achzib adadah adah adam adamah adami adadrimmon admah adramyttium adria
adullam aenon ahava ahlab ai aiath aija aijalon akrabbim alemeth alexandria
almon aloth amad amam ammah ammon amphipolis anab anaharath anathoth antioch
antipatris aphek aphekah aphik apollonia ar arab arabia araboth arad aram
ararat arba arbathite archelais argob ariel arimathea armageddon armenia
arnon aroer arpad arphaxad arvad ashdod ashdodpisgah asher ashkelon ashtaroth
assos assyria ataroth athach athens attalia ava aven avim avith azal azekah
azmaveth azmon aznoth azzah
baal baalbek baalath baalathbeer baale baalgad baalhamon baalhazor baalhermon
baalmeon baalpeor baalperazim baalshalisha baaltamar baalzephon babel babylon
baca bahurim bamoth basan bashan beersheba beirut bela ben bene beneberak
benejaakan berea bered berothai berothah besor bethabara bethanath bethany
betharabah betharbel bethaven bethazmaveth bethbaalmeon bethbarah bethbiri
bethcar bethdagon bethel bethemek bethenoth bethharam bethhogla bethhoron
bethjesimoth bethlehem bethmaacah bethmarcaboth bethmeon bethnimrah bethpalet
bethpazzez bethpeor bethphage bethphelet bethrapha bethrehob bethsaida bethshan
bethshean bethshemesh bethtappuah bethuel bethzur betonim bezek bezer bithron
bithynia bohan boscath bozez bozkath bozrah brook
cabbon cabul caesarea calneh calno calvary cana canaan caphtor cappadocia
carchemish carmel cenchrea chaldea cherith chezib chios chushan cilicia colosse
colossae corinth crete cush cuthah cyprus cyrene
damascus dan debir decapolis derbe dibon dibongad dimon dinhabah dion dophkah
dor dothan dumah dura
ebal ebenezer eden eder edom edrei eglaim eglon egypt ekron elah elam elath
elealeh eleph elim emmaus endor engedi enhaddah enhakkore enharod enhazor
enmishpat enrimmon enshemesh ephes ephesus ephraim ephrath erech eshtaol
eshtemon etam eth ethbaal ethiopia euphrates
gad gadarenes galilee gath gaza geba gebal geder gederah gederoth gederothaim
gedor gennesaret gerar gerasa gerizim geshur gethsemane gezer gibeah gibeon
gihon gilboa gilead gilgal girgash gittaim gob golan golgotha gomorrah goshen
gozan greece gur gurhaal
hachilah hadrach halah halak halhul ham hamath hammoth hanes haran hararite
hareth harod harosheth havilah havoth hazarmaveth hazeroth hazor helbah helbon
heliopolis hena hepher heres hermon heshbon hethlon hiddekel hilen hinnom hobah
holon horeb horhaggidgad horonaim hormah
iconium idumaea idumea iim ijim ijon illyricum immer india ionia iron ishmaelia
israel issachar italy ithnan itturaea ituraea iye
jabbok jabesh jaffa jahniel janohah janum japho jarmuth jattir jazer jazzer
jearim jebus jegar jehoshaphat jericho jerusalem jeshanah jeshurun jezreel
jiphtah jiphthahel jokmeam jokneam joktheel joppa jordan jotbah jotbathah
judah judea
kabzeel kadesh kadeshbarnea kanah karkor karnaim kartah kattath kebar kedesh
keilah kenath kidron kinah kir kiriath kirjath kishon kittim
lachish lahai lahairoi laish laodicea lasea lasha lebo lebanon leshem libnah
libya lod lubim ludim luhith luz lycaonia lycia lydda lydia lystra
maacah maarath maaseiah machpelah madmenah madian madmen madon magdala mahanaim
makaz makheloth makkedah mamre manahath maon mara marah mareshah masrekah
medeba medes media megiddo mella memphis meonenim meribah merom mesha meshech
mesopotamia michmash midian migdal migdol miletus millo misraim mispah mitylene
mizpah mizpeh moab moladah moria moriah mozah
naamah naaran naarath naioth naphtali nazareth neapolis nebo negeb negev neiel
nephtoah nicopolis nile nineveh no nob nod noph
olivet olives ono ophel ophir ophni ophrah
padanaram palestine pamphylia paphos paran parthia patara pathros patmos
pelusium peniel penuel peor peraea perea perga pergamos pergamum persia pethor
pharpar phenice phenicia philadelphia philippi philistia phoenicia phrygia
pibeseth pihahiroth pisidia pisgah pithom pontus ptolemais puteoli
rabbah rabbath raamah raamses rachel ragau ramah ramath ramathlehi ramathaim
rameses ramoth raphia raphon rathamin reeds rephaim resen reuben rhegium
rhodes riblah rimmon rogelim rome
salamis salcah salem samaria samos samothrace sardis sarepta seir selah
seleucia senaah seneh senir sephar sepharad shaalabbim shaalim sharon shaveh
sheba shechem shem shenir shephela shiloh shimron shinar shittim shunem shur
shushan sichem sidon siloah siloam simeon sinai sinim sion sippar smyrna sodom
spain succoth susa sychar sychem syene syria
taanach taanathshiloh taberah tabor tadmor tahapanes tahpanhes tamar tarshish
tarsus tekoa tema teman thebez thessalonica thrace thyatira tiberias tigris
timnah timnath tirzah tob togarmah tophel tophet trachonitis troas trogyllium
tyre
ulai uphaz ur urartu urfa
wilderness
zaanan zair zarethan zebulun zela zelah zelzah zemaraim zephath zephathah
zer zered zereth zidon ziklag zin zion ziph ziz zoan zoar zobah zoheleth zophim
zorah zuph
""".lower().split()

def main():
    # Load concordance
    print("Loading concordance...")
    with open("concordance.json", 'r', encoding='utf-8') as f:
        concordance = json.load(f)
    
    indexed = set(concordance['concordance'].keys())
    print(f"  {len(indexed)} indexed words")
    
    # Filter to only words that are in the concordance and not excluded
    # Also remove pure places from people list
    people = [p for p in set(BIBLICAL_PEOPLE) if p in indexed and p not in EXCLUDE_WORDS and p not in PLACES_NOT_PEOPLE]
    places = [p for p in set(BIBLICAL_PLACES) if p in indexed and p not in EXCLUDE_WORDS]
    
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
