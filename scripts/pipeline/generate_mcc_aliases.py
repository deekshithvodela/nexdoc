"""
Script: generate_mcc_aliases.py
Purpose: Generate alias mappings for raw MCC allotment college names and populate reference/alias-to-canonical.json
"""

import json
import re

RAW_CUTOFFS_PATH = 'reference/raw_college_cutoffs_mapping.json'
ALIAS_REGISTRY_PATH = 'reference/alias-to-canonical.json'
MASTER_COLLEGES_PATH = 'reference/master-lists-of-colleges.json'

INDIAN_STATES = {
    'andaman', 'nicobar', 'andhra', 'pradesh', 'arunachal', 'assam', 'bihar', 'chandigarh', 
    'chhattisgarh', 'dadra', 'nagar', 'haveli', 'daman', 'diu', 'delhi', 'goa', 'gujarat', 
    'haryana', 'himachal', 'jammu', 'kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 
    'lakshadweep', 'madhya', 'maharashtra', 'manipur', 'meghalaya', 'mizoram', 'nagaland', 
    'odisha', 'orissa', 'puducherry', 'pondicherry', 'punjab', 'rajasthan', 'sikkim', 'tamil', 
    'nadu', 'telangana', 'tripura', 'uttar', 'uttarakhand', 'uttaranchal', 'west', 'bengal'
}

def clean_name(name):
    if not name: return ''
    n = name.lower()
    n = re.sub(r'(?<=\b[a-z])\.(?=[a-z]\b)', '', n)
    n = re.sub(r'[^\w\s]', ' ', n)
    n = ' '.join(n.split())
    while re.search(r'\b([a-z])\s+([a-z])\b', n):
        n = re.sub(r'\b([a-z])\s+([a-z])\b', r'\1\2', n)
    return ' '.join(n.split())

def expand_abbreviations(text):
    t = clean_name(text)
    t = re.sub(r'\baiims\b', 'all india institute of medical sciences', t)
    t = re.sub(r'\bjipmer\b', 'jawaharlal institute of postgraduate medical education and research', t)
    t = re.sub(r'\bgovt\b|\bgov\b', 'government', t)
    t = re.sub(r'\bmed\b', 'medical', t)
    t = re.sub(r'\binst\b|\binstt\b|\binstitut\b', 'institute', t)
    t = re.sub(r'\bcol\b|\bcollage\b|\bcoll\b', 'college', t)
    t = re.sub(r'\bhosp\b|\bhospt\b', 'hospital', t)
    t = re.sub(r'\bres\b', 'research', t)
    t = re.sub(r'\bsciences\b|\bsci\b|\bsce\b', 'science', t)
    t = re.sub(r'\bcolleges\b', 'college', t)
    t = re.sub(r'\binstitutes\b', 'institute', t)
    t = re.sub(r'\bhospitals\b', 'hospital', t)
    t = re.sub(r'\bdeogarh\b', 'deoghar', t)
    t = re.sub(r'\brai bareli\b|\braebarely\b', 'raebareli', t)
    t = re.sub(r'\bsholapur\b', 'solapur', t)
    t = re.sub(r'\bbanglore\b', 'bangalore', t)
    t = re.sub(r'\bmangaluru\b', 'mangalore', t)
    t = re.sub(r'\bpuducherry\b|\bpondicherry\b', 'puducherry', t)
    t = re.sub(r'\belamkara\b', 'kochi', t)
    return ' '.join(t.split())

# Specific manual overrides for shorthand raw MCC allotment strings
MCC_MANUAL_OVERRIDES = {
    "aiims new delhi aiims ansari nagar east aurobindo marg new delhi 110029 delhi nct 110029": "All India Institute of Medical Sciences, New Delhi",
    "atal bihari vajpayee government medical college vidisha nh 86 infront of khel parisar sanchi road vidisha madhya pradesh 464001": "Atal Bihari Vajpayee Government Medical College, Vidisha",
    "autonomous state medical college lalitpur up amarpur galla mandi jhansi road lalitpur uttar pradesh 284403": "Autonomous State Medical College, Lalitpur",
    "bj government medical college pune sassoon hospital compound near pune railway station jp narayan road pune maharashtra 411001": "BJ Medical College, Pune",
    "esi mc pgims r banglore esicmc and pgimsr rajajinagar bengaluru karnataka 560010": "Employees State Insurance Corporation Medical College, Bangalore",
    "esic medical college hyderbad sanathnagar hyderabad telangana 500038": "ESIC Medical College, Sanathnagar, Hyderabad",
    "esic pgimsr joka kolkata wb diamond harbour road post office joka kolkata 700104 west bengal 700104": "ESIC Medical College and PGIMSR, Joka, Kolkata",
    "gmc manjeri kerala government medical college manjeri malappuram kerala 676121": "Government Medical College, Manjeri",
    "gmc shahjhanpur autonomous state medical college allied pandit ram prasad bismil hospital shahjahanpur uttar pradesh uttar pradesh 242001": "Autonomous State Medical College Society, Shahjahanpur",
    "gmers medical college morbi gibson middle school opp railway station morbi gujarat 363641": "GMERS Medical College, Morbi",
    "government medical college ambernath survey no 128 jambhulgaon road ambernath west district thane maharashtra 421505": "Government Medical College, Ambernath",
    "government medical college banswara rajasthan madareshwar ratlam road banswara rajasthan 327001": "Government Medical College, Banswara",
    "government medical college hanumangarh ganganagar sangria bypass road hanumangarh junction rajasthan 335512": "Government Medical College, Hanumangarh",
    "government medical college hingoli government medical college washim road balsond hingoli maharashtra 431513": "Government Medical College, Hingoli",
    "government medical college jalna government medical college global gurukul school in front of sushiladevi lawns ambad mantha bypas maharashtra 431213": "Government Medical College, Jalna",
    "government medical college kodangal survey number 51 kokat besides mother and child hospital tandur vikarabad": "Government Medical College, Kodangal",
    "government medical college konni government medical college konni kummannoor po konni pathanamthitta 689691 kerala 689691": "Government Medical College, Konni",
    "government medical college latur government medical college latur behind old railway station near marwadi rajasthan vidyalaya lat maharashtra 413512": "Government Medical College, Latur",
    "government medical college maheshwaram telangana biet college campus mangalpally village ibrahimpatnam rangareddy district telangana 501510": "Government Medical College, Maheshwaram",
    "government medical college miraj pandharpur road miraj tal miraj dist sangli maharashtra 416410": "Government Medical College, Miraj",
    "government medical college nilgiris no 1 indu nagar mysore road udhagamandalam nilgiris district tamil nadu 643005": "Government Medical College, Nilgiris",
    "government medical college omandurar government medical college omandurar government estate walaja road chennai 600 002 tamil nadu 600002": "Government Medical College, Omandurar",
    "government medical college quthbullapur government medical college quthbullapur plot a2 2b ecil cross roads kushaiguda hyderabad medch telangana 500062": "Government Medical College, Quthbullapur",
    "government medical college rajnandgaon bharat ratna late shri atal bihari vajpayee memorial medical college pendri rajnandgaon chhattisg chhattisgarh 491441": "Government Medical College, Rajnandgaon",
    "government medical college sangareddy opp town police station netaji nagar sangareddy district telangana 502001 telangana 502001": "Government Medical College, Sangareddy",
    "government medical college tiruppur 18 dharapuram road tiruppur tamilnadu 641608 tamil nadu 641608": "Government Medical College, Tiruppur",
    "govt medical college kottayam gandhinagar po kottayam kerala 686008 kerala 686008": "Government Medical College, Kottayam",
    "govt medical college nagaur bikaner road nagaur gmcnagaur gmail com rajasthan 341001": "Government Medical College, Nagaur",
    "govt medical college patiala sangrur road government medical college patiala punjab 147001": "Government Medical College, Patiala",
    "govt medical college sirohi rajasthan sirohi shivganj highway near ambeshwar village kolar tehsil sivganj dist sirohi rajasthan 307030": "Government Medical College, Sirohi",
    "gvmc villupuram the dean government villupuram medical college trichy trunk road mundiyampakkam villupuram tamil nadu 605601": "Government Villupuram Medical College, Villupuram",
    "karnatak inst of medical sc hubli vidyanagar hubballi karnataka 580021": "Karnatak Institute of Medical Sciences, Hubli",
    "maharaja kc gajapati mc brahmapur mkcg medical college campus berhampur ganjam odisha 760004": "MKCG Medical College, Berhampur",
    "medical college baroda government medical college baroda anandpura vadodara pin no 390001 gujarat 390001": "Government Medical College, Baroda",
    "mgm medical college aurangabad n 6 cidco chhatrapati sambhajinagar aurangabad maharashtra 431003": "MGM Medical College, Aurangabad",
    "mursidabad mc hospital mursidabad station road po and ps berhampore dist murshidabad west bengal 742101": "Murshidabad Medical College & Hospital, Murshidabad",
    "pt ddu medical college rajkot civil hospital campus jamnagar road rajkot 360001 gujarat 360001": "Pandit Deendayal Upadhyay Medical College, Rajkot",
    "rajah muthiah medical college annamalai universit government medical college and hospital cuddalore district erstwhile rajah muthiah medical college tamil nadu 608002": "Government Erode Medical College & Hospital, Perundurai",
    "sarat chandra chattopadhyay govt medical college hospital uluberia uluberia dist howrah west bengal 711315": "Sarat Chandra Chattopadhyay Government Medical College & Hospital, Uluberia",
    "shilong medical college meghalaya pasteur hills lawmali road shilong east khasi hills meghalaya": "Shillong Medical College, Shillong",
    "siddartha medical college vijayawada beside new government general hospital gunadala vijayawada andhra pradesh 520008": "Siddhartha Medical College, Vijayawada",
    "sri krishna medical college muzaffarpur umanagar muzaffarpur bihar 842004": "Sri Krishna Medical College, Muzaffarpur",
    "swami ramanand tirth rural mc ambajogai swami ramnand teerth rural government medical college ambajogai dist beed maharashtra pin 431517 maharashtra 431517": "Swami Ramanand Teerth Rural Medical College, Ambajogai",
    "uttaranchal f hosp trust mc haldwani government medical college rampur road haldwani distt nainiatl uttarakhand 263139": "Government Medical College, Haldwani",
    "aarupadai veedu medical college and hospt puducherry pondy cuddalore main road kirumampakkam puducherry puducherry 607403": "Jawaharlal Institute of Postgraduate Medical Education and Research, Puducherry",
    "aiims bibi nagar hyderabad aiims bibinagar hyderabad metropolitan region telangana 508126 telangana 508126": "All India Institute of Medical Sciences, Bibinagar",
    "bharati vidyapeeth du medical college dhankawadi pune satara road pune maharashtra 411043": "Bharati Vidyapeeth University Medical College, Pune",
    "brd medical college gorakhpur maharajganj road gorakhpur uttar pradesh 273013": "BRD Medical College, Gorakhpur",
    "bv deemed uni med college and hos sangli sangli miraj road wanlesswadi sangli maharashtra maharashtra 416416": "Bharati Vidyapeeth Deemed University Medical College & Hospital, Sangli",
    "chettinad hos and res inst kancheepuram rajiv gandhi salai kelambakkam chengalpattu district tamil nadu 603103": "Shri Sathya Sai Medical College and Research Institute, Kancheepuram",
    "esic medical college and pgimsr chennai ashok pillar road kk nagar chennai tamil nadu 600078": "ESIC Medical College and Hospital, K.K. Nagar, Chennai",
    "esic medical college hospital andheri central road midc andheri east mumbai": "ESIC Medical College and Hospital, Andheri",
    "esic medical college hospital beltola guwahati pir ajan fakir road beltola guwahati assam": "ESIC Medical College and Hospital, Beltola",
    "esic medical college hospital jaipur laxmi nagar ajmer road sodala jaipur": "ESIC Medical College and Hospital, Jaipur",
    "esic medical college naroda bapunagr ahmedabad ba punagar near naroda railway crosing himmatnagar highway po kubernagar": "ESIC Medical College, Naroda, Bapunagar, Ahmedabad",
    "gmers medical college navsari adarsh nivasi shala campus at khambhlav po sultanpur via abrama ta jalalpore dist navsar gujarat 396406": "GMERS Medical College, Navsari",
    "government medical college and hospital keonjhar at kabitra near dd college keonjhargarh ps town police station dist keonjhar odisha odisha 758001": "Dharanidhar Medical College and Hospital, Keonjhar",
    "govt mohan kumaramangalam mc salem majeera kollappatti salem steel plant road salem 636030 tamilnadu tamil nadu 636030": "Govt. Mohan Kumaramangalam Medical College, Salem",
    "inst of med sciences bhu varanasi institute of medical sciences banaras hindu university uttar pradesh 211005": "Heritage Institute of Medical Sciences, Varanasi",
    "jr medical college and hospital tamil nadu chennai trichy nh 45 kiledaiyalam tindivanam taluk villupuram district tamil nadu 604302": "ACS Medical College and Hospital, Chennai",
    "kasturba medical college manipal univ mangalore light house hill road mangalore india karnataka 575001": "Kasturba Medical College, Mangalore",
    "krishna inst of med scie karad karad dist satara maharashtra state maharashtra 415110": "Krishna Institute of Medical Sciences, Karad",
    "lokmanya tilak municipal mc mumbai dr babasaheb ambedkar road sion mumbai maharashtra 400022": "Lokmanya Tilak Municipal Medical College, Sion, Mumbai",
    "maharaja jitendra narayan medical college and hospital coochbehar vivekananda street pilkhana beside panchanan barma university coochbehar west bengal 736101": "Coochbehar Government Medical College & Hospital, Coochbehar",
    "maharani laxmi bai medical coll jhansi mlb medical college kanpur road jhansi uttar pradesh 284128": "Maharani Laxmi Bai Medical College, Jhansi",
    "mahatma gandhi mission medical college vashi navi mumbai sector 30 vashi navi mumbai maharashtra 400703": "Mahatma Gandhi Mission Medical College, Vashi",
    "medinirai medical college previously known as palamu medical college palamu pokhraha khurd po rajwadih ps medininagar dist palamu jharkhand 822118": "Palamu Medical College, Palamu",
    "meenakshi medical college hospital and research institute kanchipuram enathur karaipettai post kanchipuram tamil nadu 631552": "Meenakshi Medical College and Research Institute, Enathur",
    "netaji subhash chandra bose mc jabalpur nagpur road jabalpur state mp pin 482003 madhya pradesh 482003": "Netaji Subhash Chandra Bose Medical College, Jabalpur",
    "sbks med inst and res centre sumandeep vidyapeeth sumandeep vidyapeeth deemed to be university campus at po piparia tal waghodia dist vadodara gujarat 391760": "Banas Medical College and Research Institute, Palanpur, Gujarat",
    "shri sathya sai medical college and research institute chennai sbv chennai campus shri sathya sai nagar ammapettai chennai tamil nadu 603108": "ACS Medical College and Hospital, Chennai",
    "srm medical college and hospital chennai srm medical college hospital and research centre potheri kattankulathur 603203 chengalpattu dist tamil nadu 603203": "ACS Medical College and Hospital, Chennai",
    "suh maulana mahmood hasan medical college saharanpur ambala road pilakhni saharanpur uttar pradesh 247001": "Shaikh-UL-Hind Maulana Mahmood Hasan Medical College, Saharanpur",
    "tamralipto government medical college hospital west bengal 227 haldia tamluk mecheda road tamluk purba medinipur west bengal 721636": "Tamralipto Government Medical College & Hospital",
    "autonomous state medical college lakhimpur kheri uttar pradesh near deokali temple saidapur bhau uttar pradesh 262701": "Autonomous State Medical College and Hospital, Lakhimpuri Kheri",
    "blde university bijapur smt bangaramma sajjan campus bm patil road vijayapura karnataka karnataka 586103": "Shri B M Patil Medical College, Hospital & Research Centre, Vijayapura (Bijapur)",
    "deben mahata government medical college hospital vill hatuara po vivekananda nagar ps purulia muffasil dist purulia pin 723147 west bengal 723147": "Government Villupuram Medical College, Villupuram",
    "dr dy patil medical college navi mumbai plot no 2 sector 7 nerul navi mumbai maharashtra maharashtra 400706": "Mahatma Gandhi Missions Medical College, Nerul, Navi Mumbai",
    "dr sc govt medical college nanded vishnupuri nanded maharashtra 431606 maharashtra 431606": "Dr. Shankarrao Chavan Government Medical College, Nanded",
    "dr ys parmar govt medical college nahan nahan district sirmaur himachal pradesh himachal pradesh 173001": "Government Medical College, Nahan, Sirmour",
    "esic medical college faridabad nh 3 nit faridabad haryana 121001": "Al Falah School of Medical Sciences & Research Centre, Faridabad",
    "esic medical college gulbarga esic medical college sedam road gulbarga karnataka 585106": "Employees State Insurance Corporation Medical College, Gulbarga",
    "esic medical college hospital bihta esic medical college and hospital bihta patna 801103 bihar 801103": "Netaji Subhas Medical College & Hospital, Amhara, Bihta, Patna",
    "gmc azamgarh up government medical college and super facility hospital chakrapanpur post office kanaila azamgarh uttar pradesh 276128": "Government Medical College & Super Facility Hospital, Azamgarh",
    "gmc bahraich kdc road bahraich 271801 uttar pradesh 271801": "Rajkiya Allopathic Medical College, Bahraich",
    "gmc dausa rajasthan gmc dausa mitrapura bhandarej mod dausa rajasthan 303303": "Government Medical College, Bharatpur, Rajasthan",
    "gmers medical college porbandar behind iti and navoday vidyalay dharampur porbandar gujarat 360578": "Government Medical College, Porbandar",
    "goverment medical college bettiah government medical college bettiah west champaran bihar 845438 bihar 845438": "Government Medical College, Bettiah",
    "goverment medical college datia near 29th battalion nh 75 datia madhya pradesh 475661": "Government Medical College, Datia",
    "goverment medical college singrauli goverment medical college villege naugadh singrauli madhya pradesh": "Government Medical College, Singrauli",
    "government medcial college gondia near nehru chowk kts hospital campus gondia maharashtra 441601": "Government Medical College, Gondia",
    "government medical college and general hospital satara government medical college and general hospital satara district civil hospital campus sadar bazar ca maharashtra 415001": "Government Medical College, Satara",
    "government medical college and hospital jajpur odisha renamed as jajati keshari medical college and hospital jajpur dean and principal government medical college and hospital jajpur renamed as maharaja jajati kesh odisha 755001": "Mahraja Jajati Keshari Medical College, Jajpur, Odhisha",
    "government medical college hospital alibag raigad government medical college of alibag alibag beach limaye wadi alibagh maharashtra 402201 maharashtra 402201": "Government Medical College, Alibag",
    "government of medical college and hospital balasore remuna balasore 756019 odisha 756019": "Government Medical College & Hospital, Balasore",
    "govt dharamapuri med coll dharmapuri nethaji bypass road dharmapuri tamil nadu 636701": "Government Dharmapuri Medical College, Dharmapuri",
    "gtmc thiruvarur master plan complex vilamal village thiruvarur tamil nadu 610004": "Thiruvarur Government Medical College, Thiruvarur",
    "jawahar lal nehru medical ajmer near patel stadium ajmer rajasthan 305001": "Jawaharlal Nehru Medical College, Ajmer",
    "jawahar lal nehru medical college belagavi jn medical college campus nehru nagar belagavi 590010 karnataka india karnataka 590010": "Belagavi Institute of Medical Sciences, Belagavi",
    "jln ims imphal prompat imphal east manipur manipur 795005": "Jawaharlal Nehru Institute of Medical Sciences, Porompet, Imphal",
    "jln medical college datta meghe wardha sawangi meghe wardha maharashtra state india maharashtra 442107": "Jawaharlal Nehru Medical College, Sawangi (Meghe), Wardha",
    "kgmc lucknow shahmina road chowk lucknow uttar pradesh 226003": "Career Institute of Medical Sciences & Hospital, Lucknow",
    "lt la m govt medical college raigarh tv tower road bendrachua raigarh chhattisgarh 496001": "Late Shri Lakhi Ram Agrawal Memorial Government Medical College, Raigarh",
    "mgm medical college indore ab road indore madhya pradesh 452001": "ESIC Medical College and Hospital, Indore",
    "mgm medical college jamshedpur dimna road mango jamshedpur jharkhand 831020": "M G M Medical College, Jamshedpur",
    "mgm medical college navi mumbai mgm medical college plot no 1 2 sector 1 kamothe navi mumbai 410 209 maharashtra 410209": "Mahatma Gandhi Missions Medical College, Kamothe, Navi Mumbai",
    "neigrihms shillong mawdiangdiang shillong east khasi hills district meghalaya 793018": "North Eastern Indira Gandhi Regional Institute of Health and Medical Sciences, Shillong",
    "phulo jhano medical college dumka phulo jhano medical college dumka jharkhand 814110": "Dumka Medical College, Dighi Dumka",
    "raja rajeswari medical college bengaluru 202 kambipura bengaluru mysuru high way kengeri hobli bangalore karnataka karnataka 560074": "National Institute of Mental Health and Neurosciences (NIMHANS), Bengaluru",
    "rajiv gandhi institute of medical sciences kadapa government medical college rims putlampalli ysr kadapa dist gmc kadapa ap andhra pradesh 516002": "Fathima Institute of Medical Sciences, Kadapa",
    "rani durgavati medical college banda rani durgavati medical college naraini road banda 210001 uttar pradesh 210001": "Government Allopathic Medical College, Banda",
    "rims ongole bhagyanagar 5th lane rims ongole prakasam district andhra pradesh andhra pradesh 523001": "Government Medical College, Ongole",
    "rnt medical college udaipur opposite court chourha udaipur rajasthan 313001": "Geetanjali Medical College & Hospital, Udaipur",
    "saveetha medical college chennai saveetha nagar thandalam chennai tamil nadu 602105": "Madha Medical College and Hospital, Thandalam, Chennai",
    "seth gs medical college mumbai acharya donde marg parel mumbai maharashtra 400012": "ESI-PGIMSR, ESI- Hospital, Parel, Mumbai",
    "sheikh bhikhari medical college hospital hazaribag formerly called as hazaribagh medical college hazaribag near central jail hazaribag jharkhand 825301": "Hazaribagh Medical College, Hazaribagh",
    "sjp medical college bharatpur rampura nh 21 sever road bharatpur rajasthan rajasthan 321001": "Government Medical College, Bharatpur, Rajasthan",
    "skims medical college bemina srinagar skims mc bemina srinagar jammu kashmir jammu and kashmir 190018": "Government Medical College, Srinagar",
    "slbs govt medical college mandi mandi at nerchowk po bhangrotu tehsil balh district mandi himachal pradesh 175021": "Shri Lal Bahadur Shastri Government Medical College, Mandi",
    "ss medical college rewa near dhobiya tanki jail road rewa madhya pradesh 486001": "Shyam Shah Medical College, Rewa",
    "uns autonomous state medical colleges jaunpur uns autonomous state medical college siddiquepur shahganj road jaunpur up uttar pradesh 222003": "Uma Nath Singh Autonomous State Medical College Society, Jaunpur",
    "vmkv medical college and hospital salem sankari main road nh 47 seeragapadi salem tamil nadu 636308": "Annapoorna Medical College & Hospital, Salem",
    "vss medical college burla ayurvihar burla sambalpur odisha 768017": "Veer Surendra Sai Institute of Medical Sciences and Research, Burla",
    "aiims bathinda jodhpur romana near giani zail singh college mandi dabwali road bathinda punjab 151001": "All India Institute of Medical Sciences, Bathinda",
    "aiims mangalagiri all india institute of medical sciences near tadepalli mangalagiri guntur dt andhra pradesh andhra pradesh 522503": "All India Institute of Medical Sciences, Mangalagiri",
    "aiims rajkot admission cell academic section first floor academic block permanent campus aiims rajkot khand gujarat 360110": "All India Institute of Medical Sciences, Rajkot",
    "autonomous state medical college society hardoi gaura danda sitapur road hardoi uttar pradesh 241001": "Autonomous State Medical College Society, Hardoi",
    "baba kinaram autonomous state medical college chandauli baba kinaram autonomous state medical college naubatpur chandauli uttar pradesh 232110": "Baba Kina Ram Autonomous State Medical College and Hospital, Chandauli",
    "bangalore medical college and research institute kr road fort bengaluru karnataka 560002": "Bangalore Medical College and Research Institute, Bangalore",
    "belgaum inst of medical sci belgaum dr br ambedkar road belagavi karnataka 590001": "Jawaharlal Nehru Medical College, Belgaum",
    "burdwan medical college burdwan burdwan medical college baburbag post rajbati dist purba bardhaman pin 713104 west bengal west bengal 713104": "Burdwan Medical College, Burdwan",
    "dhubri medical college assam po jhagrarpar spo dhubri assam pin 783325 assam 783325": "Dhubri Medical College, Dhubri",
    "dr rajendra prasad mc tanda dr rajendra prasad govt medical college kangra at tanda hp himachal pradesh 176002": "Dr. Rajendar Prasad Government Medical College, Tanda, H.P",
    "dr ram manohar lohia inst of med sce lucknow vibhuti khand gomti nagar lucknow uttar pradesh 226010": "Dr. Ram Manohar Lohia Institute of Medical Sciences, Lucknow",
    "dr sn medical college jodhpur residency road shastri nagar jodhpur rajasthan 342 003 rajasthan 342003": "Dr. S.N. Medical College, Jodhpur",
    "dr vaishampayam memorial mc sholapur in front of district civil court solapur maharashtra 413003": "Dr Vaishampayan Memorial Medical College, Solapur",
    "dy patil university school of medicine taluka maval pune survey no 124 126 midc road ambi taluka maval dist pune 410506": "DY Patil University, School of Medicine",
    "employees state insurance corporation medical college alwar esic medical college and hospital desula mia alwar rajasthan india 301030 rajasthan 301030": "Employees State Insurance Corporation Medical College, Alwar",
    "goverment medical college sheopur mp gmc sheopur village nagda near nageshwar temple dist sheopur mp": "Government Medical College, Sheopur",
    "government medical college amravati government medical college district women hospital campus daffrin shrikrishna peth amravati maharashtra 444601": "Government Medical College, Amravati",
    "government medical college and district general hospital ratnagiri hodekar road udyamnagar patwardhanwadi ratnagiri maharashtra 415612 maharashtra 415612": "Government Medical College and District Hospital, Ratnagiri",
    "government medical college and esic hospital coimbatore kamarajar road varadharajapuram singanallur coimbatore tamil nadu 641015": "Government Medical College & ESIC Hospital, Coimbatore, Tamil Nadu",
    "government medical college bhadradri kothagudem besides sammakka saarakka temple opp ksm petrol bunk end of 6th battalion rd palvancha telangana telangana 507118": "Government Medical College, Bhadradri Kothagudem",
    "government medical college chittorgarh government medical college chittorgarh bojunda udaipur road chittorgarh rajasthan 312025": "Government Medical College, Chittorgarh",
    "government medical college esic kollam parippally kollam 691574 kerala 691574": "Government Medical College, Parippally, Kollam",
    "government medical college karimnagar telangana the principal government medical college karimnagar jagtial nh 563 kothapalli karimnagar telangana 505451": "Chalmeda Anand Rao Institute of Medical Sciences, Karimnagar",
    "government medical college machilipatnam kara agraharam near radar station machilipatnam krishna district andhra pradesh 521002 andhra pradesh 521002": "Government Medical College, Machilipatnam",
    "government medical college nashik hindu hruday samrat vandaniya balasaheb thakare hospital and bytco hospital near durga mata mandir m maharashtra 422214": "Government Medical College, Nashik",
    "government medical college nirmal beside divya garden divya nagar nirmal telangana 504106": "Government Medical College, Nirmal",
    "government medical college virudhunagar 1 collectorate master plan complex kooraikundu village virudhunagar tamil nadu 626002": "Government Medical College, Virudhunagar",
    "government medical college yadadri pagadipally bhongir yadadri bhuvanagiri telangana 508116": "Government Medical College, Yadadri",
    "govt medical college baramati plot no p107 midc area opposite women hospital baramati taluka baramati district pune maharashtra 413133": "Government Medical College & Hospital, Baramati",
    "govt medical college barmer rajasthan nh 15 jaisalmer road village jalipa barmer rajasthan 344001": "Government Medical College, Barmer",
    "govt medical college basti rampur tahsil sadar basti basti uttar pradesh 272124": "Government Medical College, Rampur, Basti",
    "govt medical college jayashankar bhupalpally manzoor nagar road besides thousand quarters jayashankar bhupalpally telangana 506169": "Government Medical College, Jayashankar Bhupalpally",
    "govt medical college karur sanapiratti village north gandhigramam karur tamilnadu tamil nadu 639004": "Government Medical College, Karur",
    "govt medical college kumuram bheem asifabad government medical college ankushapur district kumuram bheem asifabad telangana telangana 504293": "Government Medical College, Kumuram Bheem Asifafabad",
    "govt medical college nalgonda office of the principal government medical collgege gandhamvari gudem slbc sagar road nalgonda tela telangana 508004": "Government Medical College, Nalgonda",
    "govt medical college rajanna sircilla government medical college near kasturba girls school peddur sircilla district rajanna sircilla telangana 505301": "Government Medical College, Rajanna Sircilla",
    "govt medical college ratlam gram banjali sailana road nh927a madhya pradesh 457001 india madhya pradesh 457001": "Dr. Laxminarayan Pandey Government Medical College, Ratlam, Madhya Pradesh",
    "govt medical college shahdol gram champa kudri road near new bus stand shahdol mp madhya pradesh 484001": "Government Medical College, Shahdol",
    "govt medical college shivpuri near katha mill gwalior bypass highway shivpuri madhya pradesh 473638": "Government Medical College, Shivpuri",
    "govt sivgangai mc sivagangai manamadurai main road keela vaniyankudi sivagangai tamil nadu 630561": "Government Sivagangai Medical College, Sivaganga",
    "grant medical coll sir jj hosp mumbai sir jj group of hospitalcompound sir jj road byculla mumbai maharashtra 400008": "Grant Medical College, Mumbai",
    "gulbarga institute of medical sciences gulbarga gulbarga institute of medical sciences veeresh nagar sedam road kalaburagi karnataka 585105": "Gulbarga Institute of Medical Sciences, Gulbarga",
    "guwahati medical college guwahati narakasur hill top bhangagarh guwahati assam 781032": "All India Institute of Medical Sciences, Guwahati",
    "inst of pg med edu research kolkata 244 ajc bose road kolkata west bengal 700020": "Institute of Postgraduate Medical Education & Research, Kolkata",
    "jhalawar medical college jhalawar nh 52 kota road jhalawar rajasthan rajasthan 326001": "Jhalawar Medical College, Jhalawar",
    "jhargram government medical college and hospital west bengal jhargram government medical college and hospital vidyasagarpally jhargram west bengal west bengal 721507": "Jhargram Government Medical College & Hospital, Jhargram",
    "jorhat medical college and hospital jorhat kushal konwar path barbheta jorhat assam 785001 assam 785001": "Jorhat Medical College & Hospital, Jorhat",
    "kokrajhar medical college hospital rangalikhata rangalikhata pt 1 kokrajhar assam 783370": "Kokrajhar Medical College",
    "mahatma gandhi medical college pondicherry sbv pondicherry campus pillaiyarkuppam puducherry 607402": "Mahatma Gandhi Institute of Medical Sciences, Sevagram, Wardha",
    "mahatma gandhi mission medical college nerul sector 8 nerul west navi mumbai maharashtra 400706": "Mahatma Gandhi Missions Medical College, Nerul, Navi Mumbai",
    "mandya inst of medical sci mandya bangalore mysore main road mandya karnataka 571401": "Mandya Institute of Medical Sciences, Mandya",
    "manipal tata medical college kadani road baridih jamshedpur east singbhum district jharkhand 831017": "Kasturba Medical College, Manipal",
    "midnapore medical college midnapur 5 vidyasagar road midnapore 721101 paschim medinipur west bengal 721101": "Midnapore Medical College, Midnapore",
    "mm inst med and research mullana mm institute of medical sciences and research mullana ambala haryana haryana 133207": "Maharishi Markandeshwar Institute of Medical Sciences & Research, Mullana, Ambala",
    "moti lal nehru medical coll allahabad principal office moti lal nehru medical college lowther road george town prayagraj uttar pradesh 211001": "Moti Lal Nehru Medical College, Allahabad",
    "nalanda medical college patna old byepass road kankerbagh patna bihar 800026": "Nalanda Medical College, Patna",
    "nalbari medical college hospital dakhingaon nalbari po dakhingaon dist nalbari ps ghograpar assam 781350": "Nalbari Medical College, Nalbari",
    "ndmc medical college delhi north delhi municipal corporation medical college and hindu rao hospital malka ganj delhi nct 110007": "Late Shri Baliram Kashyap Memorial NDMC Government Medical College, Jagdalpur",
    "pragjyotishpur medical college guwahati rk mission birubari guwahati": "Pragjyotishpur Medical College",
    "raichur inst of medical sci raichur raichur institute of medical sciences industrial area hyderabad road raichur karnataka 584102 karnataka 584102": "Raichur Institute of Medical Sciences, Raichur",
    "rajarshee chhatrapati shahu maharaj government medical college kolhapur rajarshee chhatrapati shahu maharaj government medical college rk nagar road shenda park kol maharashtra 416012": "Rajashree Chatrapati Shahu Maharaj Government Medical College, Kolhapur",
    "rampurhat govt medical college rampurhat rampurhat government medical college and hospital po rampurhat ps rampurhat pin 731224 dist birbhum west bengal 731224": "Rampurhat Government Medical College & Hospital, Rampurhat",
    "rangaraya medical college kakinada pithapuram road kakinada andhra pradesh 533003": "Rangaraya Medical College, Kakinada",
    "rims srikakulam balaga srikakulam andhra pradesh 532001": "Great Eastern Medical School and Hospital, Srikakulam",
    "sagar dutta medical college hospital kolkata 578 bt road kamarhati kolkata west bengal 700058": "Bundelkhand Medical College, Sagar",
    "shimoga inst of medical sci shimoga sagar road mcgann hospital campus shivamogga karnataka 577201": "Shimoga Institute of Medical Sciences, Shimoga",
    "shri bhausaheb hire govt mc dhule shri bhusaheb hire government medical college malegaon road chakkarbardi area dhule maharashtra 424002": "Sri Bhausaheb Hire Government Medical College, Dhule",
    "sri siddhartha academy t begur sri siddhartha institute of medical sciences and research centre t begur nelamangala taluk bangalor karnataka 562123": "Sri Siddhartha Institute of Medical Sciences & Research Centre, Bangalore",
    "sri venkateswara medical college tirupati near vivekandanda circle alipiri road tirupati andhra pradesh 517507": "SVIMS - Sri Padmavathi Medical College for Women, Alipiri Road, Tirupati",
    "tinsukia medical college hospital tinsukia lohari bangali gaon tinsukia assam 786146": "Tinsukia Medical College, Assam",
    "uttar pradesh university of medical sciences saifai etawah saifai etawah uttar pradesh 206130": "Uttar Pradesh University of Medical Sciences, Etawah",
    "vardhman institute of medical sciences nalanda bmims pawapuri nalnada bihar 803115": "Bhagwan Mahavir Institute of Medical Sciences, Pawapuri",
    "zoram medical college falkawn academic block zoram medical college and hospital falkawn aizawl district mizoram 796005 mizoram 796005": "Zoram Medical College, Mizoram",
    "mysore med.& research inst. mysore": "Mysore Medical College and Research Institute, Mysore",
    "mysore medical college and research institute": "Mysore Medical College and Research Institute, Mysore",
    "bangalore med. college bangalore": "Bangalore Medical College and Research Institute, Bangalore",
    "kgmc lucknow": "King George's Medical University, Lucknow",
    "king george's medical university": "King George's Medical University, Lucknow",
    "s c b medical college cuttack": "S.C.B. Medical College, Cuttack",
    "s.c.b. medical college cuttack": "S.C.B. Medical College, Cuttack",
    "s m s medical college jaipur": "S.M.S. Medical College, Jaipur",
    "medical college kolkata": "Medical College, Kolkata",
    "medical college, kolkata, 88, college street, kolkata-700073, west bengal, 700073": "Medical College, Kolkata",
    "inst of pg med edu & research, kolkata, 244 ajc bose road, kolkata, west bengal, 700020": "Institute of Postgraduate Medical Education & Research, Kolkata",
    "esic medical college, faridabad, nh 3 nit faridabad, haryana, 121001": "Employees State Insurance Corporation Medical College, Faridabad",
    "indira gandhi medical college & ri, puducherry, vazhudavour road, kadirkamam, puducherry, 605009": "Indira Gandhi Medical College & Research Institute, Puducherry",
    "amrita school of dentistry, kochi, amrita school of dentistry, amrita institute of medical sciences (aims), aims ponekkara p.o, kochi, kerala, 682041": "Amrita School of Medicine, Elamkara, Kochi",
    "maharaja jitendra narayan medical college and hospital coochbehar, vivekananda street, pilkhana, beside panchanan barma university, coochbehar, west bengal, 736101": "Coochbehar Government Medical College & Hospital, Coochbehar",
    "government medical college & hospital, jalpaiguri, hospital road, jalpaiguri, west bengal- 735101, west bengal, 735101": "Government Medical College and Hospital, Jalpaiguri",
    "jhargram government medical college and hospital, west bengal, jhargram government medical college and hospital, vidyasagarpally, jhargram, west bengal., west bengal, 721507": "Jhargram Government Medical College & Hospital",
    "dr. r. ahmed dent.coll & hosp, kolkata, 114 ajc bose road, west bengal, 700014": "Dr. R Ahmed Dental College & Hospital, Kolkata",
    "kasturba medical college, manipal univ., mangalore, light house hill road, mangalore, india, karnataka, 575001": "Kasturba Medical College, Mangalore",
    "kasturba medical college, manipal univ., manipal, madhav nagar, manipal, karnataka state india, karnataka, 576104": "Kasturba Medical College, Manipal",
    "esic pgimsr, joka, kolkata, wb, diamond harbour road post office joka kolkata 700104, west bengal, 700104": "Employees State Insurance Corporation Medical College, Joka, Kolkata",
    "tamralipto government medical college & hospital, west bengal, 227 haldia tamluk mecheda road, tamluk, purba medinipur, west bengal, 721636": "Tamralipto Government Medical College and Hospital, Tamluk",
    "government medical college and hospital, keonjhar, at-kabitra, near dd college, keonjhargarh, ps- town police station, dist-keonjhar, odisha, odisha, 758001": "Dharanidhar Medical College and Hospital, Keonjhar",
    "jipmer karaikal, jipmer academic campus, fci link road, kovilpathu, karaikal - 609602, puducherry, 609602": "Jawaharlal Institute of Postgraduate Medical Education and Research, Karaikal",
    "indira gandhi institute of dental sciences, pondicherry, sbv pondicherry campus, pillaiyarkuppam, , puducherry, 607402": "Indira Gandhi Institute of Dental Sciences, Pondicherry",
    "dy patil university school of medicine, taluka maval, pune, survey no 124 & 126 MIDC Road, ambi, taluka maval, dist pune- 410506": "DY Patil University, School of Medicine",
    "prafulla chandra sen government medical college & hospital, arambagh, arambagh, hooghly, west bengal, 712601": "Prafulla Chandra Sen Government Medical College & Hospital, Arambagh",
    "sarat chandra chattopadhyay govt. medical college & hospital, uluberia, uluberia, dist-howrah, west bengal, 711315": "Sarat Chandra Chattopadhyay Government Medical College & Hospital, Uluberia",
    "karnatak inst. of medical sci. hubli": "Karnatak Institute of Medical Sciences, Hubli",
    "mandya inst. of medical sci., mandya": "Mandya Institute of Medical Sciences, Mandya",
    "shimoga inst. of medical sci., shimoga": "Shimoga Institute of Medical Sciences, Shimoga",
    "raichur inst. of medical sci., raichur": "Raichur Institute of Medical Sciences, Raichur",
    "koppal institute of medical sciences": "Koppal Institute of Medical Sciences, Koppal",
    "m k c g medical college berhampur": "MKCG Medical College, Berhampur",
    "l l r m medical college meerut": "L.L.R.M. Medical College, Meerut",
    "v s s medical college burla": "Veer Surendra Sai Institute of Medical Sciences and Research, Burla",
    "t d medical college allappuzha": "Government Medical College, Alappuzha",
    "s s medical college rewa": "Shyam Shah Medical College, Rewa",
    "m g d c hospital puducherry": "Mahatma Gandhi Post Graduate Institute of Dental Sciences, Puducherry",
    "r i m s srikakulam": "Rajiv Gandhi Institute of Medical Sciences, Srikakulam",
    "r i m s ongole": "Rajiv Gandhi Institute of Medical Sciences, Ongole",
    "g.s.v.m. medical college, kanpur": "G.S.V.M. Medical College, Kanpur",
    "dr. vaishampayam memorial m.c., sholapur": "Dr Vaishampayan Memorial Medical College, Solapur",
    "dr.s.c.govt medical college, , nanded": "Dr. Shankarrao Chavan Government Medical College, Nanded",
    "guwahati medical college, guwahati": "Gauhati Medical College, Guwahati",
    "esi-mc&pgims&r, banglore": "Employees State Insurance Corporation Medical College, Bangalore",
    "dr. dyp edu. soc. deemed uni., kolhapur": "Dr. D Y Patil Medical College, Kolhapur",
    "dr. ys parmar govt. medical college, nahan": "Dr. Y.S. Parmar Government Medical College, Nahan",
    "deben mahata government medical college & hospital": "Deben Mahata Government Medical College & Hospital",
    "gmc dausa rajsthan": "Government Medical College, Dausa",
    "gmc jangaon": "Government Medical College, Jangaon",
    "gmc karauli": "Government Medical College, Karauli",
    "gmc kamareddy": "Government Medical College, Kamareddy",
    "gmc, azamgarh, up": "Government Medical College and Super Facility Hospital, Azamgarh",
    "gmc, shahjhanpur": "Autonomous State Medical College Society, Shahjahanpur",
    "goverment medical college nandurbar mahararastra": "Government Medical College, Nandurbar",
    "government medical college and general hospital, satara": "Government Medical College, Satara",
    "govt. dharatapuri med coll, dharmapuri": "Government Dharmapuri Medical College, Dharmapuri",
    "gtmc, thiruvarur": "Government Thiruvarur Medical College, Thiruvarur",
    "gadag institute of medical sciences": "Gadag Institute of Medical Sciences, Gadag",
    "goverment medical college sheopur, m.p": "Government Medical College, Sheopur",
    "goverment medical college, bettiah": "Government Medical College, Bettiah",
    "goverment medical college, datia": "Government Medical College, Datia",
    "goverment medical college, singrauli": "Government Medical College, Singrauli",
    "government medcial college, gondia": "Government Medical College, Gondia",
    "government medical college mahasamund chhattisgarh": "Government Medical College, Mahasamund",
    "government medical college and district general hospital, ratnagiri": "Government Medical College, Ratnagiri"
}

def extract_master_cities(master_colleges):
    cities = set()
    EXCLUDE = {'hospital', 'research', 'institute', 'medical', 'college', 'sciences', 'and', 'the', 'of', 'for', 'society', 'trust', 'campus', 'centre', 'center', 'university', 'deemed', 'autonomous', 'govt', 'government', 'state', 'india', 'all', 'district', 'post', 'street', 'road', 'nagar', 'near', 'opp', 'opposite', 'behind', 'beside', 'block', 'building', 'complex', 'hall', 'nh', 'pin', 'pincode', 'dist', 'po', 'ps', 'taluk', 'taluka', 'distt', 'sector', 'marg', 'new', 'old', 'east', 'west', 'north', 'south', 'central', 'general', 'super', 'speciality', 'specialty', 'care', 'health', 'welfare', 'family', 'memorial', 'national', 'international', 'reg', 'regional', 'dental', 'ayurvedic', 'homeopathic', 'nursing', 'pharmacy'}.union(INDIAN_STATES)
    for m in master_colleges:
        parts = [p.strip() for p in m.split(',')]
        if len(parts) > 1:
            for p in parts[1:]:
                clean_p = re.sub(r'[^a-zA-Z\s]', '', p).lower().strip()
                if clean_p and clean_p not in EXCLUDE and len(clean_p) >= 3:
                    for w in clean_p.split():
                        if w not in EXCLUDE and len(w) >= 3 and not w.isdigit():
                            cities.add(w)
    return cities

def is_city_compatible(raw_str, candidate_m, master_cities):
    r_low = raw_str.lower()
    c_low = candidate_m.lower()

    for city in master_cities:
        if city in r_low and city not in c_low:
            # Synonyms & exemptions
            if city in ['pondicherry', 'puducherry'] and any(x in c_low for x in ['pondicherry', 'puducherry']): continue
            if city in ['mangalore', 'mangaluru'] and any(x in c_low for x in ['mangalore', 'mangaluru']): continue
            if city in ['kochi', 'elamkara'] and any(x in c_low for x in ['kochi', 'elamkara']): continue
            if city == 'puri' and ('dharmapuri' in r_low or 'tripura' in r_low or 'kanpur' in r_low): continue
            return False
    return True

def main():
    raw_cutoffs = json.load(open(RAW_CUTOFFS_PATH))
    master_colleges = json.load(open(MASTER_COLLEGES_PATH))

    master_cities = extract_master_cities(master_colleges)

    # Re-initialize clean alias registry
    alias_registry = {}

    master_exp_map = {expand_abbreviations(m): m for m in master_colleges}
    master_base_map = {expand_abbreviations(m.split(',')[0].strip()): m for m in master_colleges}

    raw_unique = sorted(list(set(x['college_name'] for x in raw_cutoffs)))
    new_aliases_added = 0

    for raw in raw_unique:
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        cand = None

        clean_raw_str = clean_name(raw)
        exp_raw_str = expand_abbreviations(raw)

        # 1. Direct manual override check
        if clean_raw_str in MCC_MANUAL_OVERRIDES:
            cand = MCC_MANUAL_OVERRIDES[clean_raw_str]
        elif exp_raw_str in MCC_MANUAL_OVERRIDES:
            cand = MCC_MANUAL_OVERRIDES[exp_raw_str]

        # Check part 0 override
        if not cand and len(parts) >= 1:
            c0 = clean_name(parts[0])
            e0 = expand_abbreviations(parts[0])
            if c0 in MCC_MANUAL_OVERRIDES: cand = MCC_MANUAL_OVERRIDES[c0]
            elif e0 in MCC_MANUAL_OVERRIDES: cand = MCC_MANUAL_OVERRIDES[e0]

        # 2. Check parts against master maps with city compatibility enforcement
        if not cand:
            for p in parts:
                exp_p = expand_abbreviations(p)
                if exp_p in master_exp_map and is_city_compatible(raw, master_exp_map[exp_p], master_cities):
                    cand = master_exp_map[exp_p]
                    break
                if exp_p in master_base_map and is_city_compatible(raw, master_base_map[exp_p], master_cities):
                    cand = master_base_map[exp_p]
                    break

        # 3. Check part combinations with city compatibility enforcement
        if not cand and len(parts) >= 2:
            for i in range(len(parts)):
                for j in range(len(parts)):
                    if i == j: continue
                    pair = expand_abbreviations(f'{parts[i]} {parts[j]}')
                    if pair in master_exp_map and is_city_compatible(raw, master_exp_map[pair], master_cities):
                        cand = master_exp_map[pair]
                        break
                if cand: break

        # 4. Fuzzy match part[1] or part[0] with strict city compatibility enforcement
        if not cand and len(parts) >= 2:
            target1 = expand_abbreviations(parts[0])
            target2 = expand_abbreviations(parts[1])
            for exp_m, m in master_exp_map.items():
                if len(target2) > 12 and target2 in exp_m and is_city_compatible(raw, m, master_cities):
                    cand = m
                    break
                if len(target1) > 12 and target1 in exp_m and is_city_compatible(raw, m, master_cities):
                    cand = m
                    break

        if cand:
            if clean_raw_str not in alias_registry:
                alias_registry[clean_raw_str] = {
                    "canonical": cand,
                    "original_display": raw
                }
                new_aliases_added += 1

    with open(ALIAS_REGISTRY_PATH, 'w') as f:
        json.dump(alias_registry, f, indent=2, ensure_ascii=False)

    print(f"MCC Aliases Generation Complete with Dynamic City Matching.")
    print(f"Total Raw MCC Names: {len(raw_unique)}")
    print(f"New Alias Entries Registered: {new_aliases_added}")
    print(f"Total Registry Entries: {len(alias_registry)}")

if __name__ == '__main__':
    main()
