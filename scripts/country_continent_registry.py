# -*- coding: utf-8 -*-
"""Comprehensive Country, Continent, and Arab League Registry for NOAA/WMO Weather Stations."""

# Mapping: Code -> (English Name, Arabic Name, Continent, Is_Arab)
# Continents: 'Arab', 'Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania', 'Antarctica'

COUNTRY_REGISTRY = {
    # === Arab League Countries (الدول العربية - 22 دولة) ===
    "EG": ("Egypt", "جمهورية مصر العربية", "Africa", True),
    "SA": ("Saudi Arabia", "المملكة العربية السعودية", "Asia", True),
    "AE": ("United Arab Emirates", "الإمارات العربية المتحدة", "Asia", True),
    "JO": ("Jordan", "المملكة الأردنية الهاشمية", "Asia", True),
    "LY": ("Libya", "دولة ليبيا", "Africa", True),
    "AG": ("Algeria", "الجمهورية الجزائرية", "Africa", True),
    "DZ": ("Algeria", "الجمهورية الجزائرية", "Africa", True),
    "MO": ("Morocco", "المملكة المغربية", "Africa", True),
    "TS": ("Tunisia", "الجمهورية التونسية", "Africa", True),
    "SU": ("Sudan", "جمهورية السودان", "Africa", True),
    "SD": ("Sudan", "جمهورية السودان", "Africa", True),
    "SY": ("Syria", "الجمهورية العربية السورية", "Asia", True),
    "IZ": ("Iraq", "جمهورية العراق", "Asia", True),
    "IQ": ("Iraq", "جمهورية العراق", "Asia", True),
    "KU": ("Kuwait", "دولة الكويت", "Asia", True),
    "KW": ("Kuwait", "دولة الكويت", "Asia", True),
    "QA": ("Qatar", "دولة قطر", "Asia", True),
    "MU": ("Oman", "سلطنة عُمان", "Asia", True),
    "OM": ("Oman", "سلطنة عُمان", "Asia", True),
    "LE": ("Lebanon", "الجمهورية اللبنانية", "Asia", True),
    "LB": ("Lebanon", "الجمهورية اللبنانية", "Asia", True),
    "BA": ("Bahrain", "مملكة البحرين", "Asia", True),
    "YM": ("Yemen", "الجمهورية اليمنية", "Asia", True),
    "YE": ("Yemen", "الجمهورية اليمنية", "Asia", True),
    "MR": ("Mauritania", "الجمهورية الإسلامية الموريتانية", "Africa", True),
    "SO": ("Somalia", "جمهورية الصومال الفيدرالية", "Africa", True),
    "DJ": ("Djibouti", "جمهورية جيبوتي", "Africa", True),
    "CN": ("Comoros", "جمهورية جزر القمر الاتحادية", "Africa", True),
    "KM": ("Comoros", "جمهورية جزر القمر الاتحادية", "Africa", True),
    "PS": ("Palestine", "دولة فلسطين", "Asia", True),
    "GZ": ("Palestine", "دولة فلسطين", "Asia", True),
    "WE": ("Palestine", "دولة فلسطين", "Asia", True),
    "IS": ("Palestine", "دولة فلسطين", "Asia", True),
    "IL": ("Palestine", "دولة فلسطين", "Asia", True),

    # === Africa (قارة أفريقيا - الدول غير العربية) ===
    "AO": ("Angola", "أنغولا", "Africa", False),
    "BC": ("Botswana", "بوتسوانا", "Africa", False),
    "BN": ("Benin", "بنين", "Africa", False),
    "BJ": ("Benin", "بنين", "Africa", False),
    "BY": ("Burundi", "بوروندي", "Africa", False),
    "CD": ("Chad", "تشاد", "Africa", False),
    "CF": ("Congo (Brazzaville)", "جمهورية الكونغو", "Africa", False),
    "CG": ("Congo (Kinshasa)", "جمهورية الكونغو الديمقراطية", "Africa", False),
    "CM": ("Cameroon", "الكاميرون", "Africa", False),
    "CV": ("Cape Verde", "الرأس الأخضر", "Africa", False),
    "EK": ("Equatorial Guinea", "غينيا الاستوائية", "Africa", False),
    "ER": ("Eritrea", "إريتريا", "Africa", False),
    "ET": ("Ethiopia", "إثيوبيا", "Africa", False),
    "GA": ("Gambia", "غامبيا", "Africa", False),
    "GB": ("Gabon", "الغابون", "Africa", False),
    "GH": ("Ghana", "غانا", "Africa", False),
    "GV": ("Guinea", "غينيا", "Africa", False),
    "GN": ("Guinea", "غينيا", "Africa", False),
    "IV": ("Cote d'Ivoire", "ساحل العاج", "Africa", False),
    "KE": ("Kenya", "كينيا", "Africa", False),
    "LI": ("Liberia", "ليبيريا", "Africa", False),
    "LT": ("Lesotho", "ليسوتو", "Africa", False),
    "LS": ("Lesotho", "ليسوتو", "Africa", False),
    "MA": ("Madagascar", "مدغشقر", "Africa", False),
    "MI": ("Malawi", "ملاوي", "Africa", False),
    "ML": ("Mali", "مالي", "Africa", False),
    "MP": ("Mauritius", "موريشيوس", "Africa", False),
    "MZ": ("Mozambique", "موزمبيق", "Africa", False),
    "NG": ("Niger", "النيجر", "Africa", False),
    "NI": ("Nigeria", "نيجيريا", "Africa", False),
    "PU": ("Guinea-Bissau", "غينيا بيساو", "Africa", False),
    "RW": ("Rwanda", "رواندا", "Africa", False),
    "SE": ("Seychelles", "سيشل", "Africa", False),
    "SC": ("Seychelles", "سيشل", "Africa", False),
    "SF": ("South Africa", "جنوب أفريقيا", "Africa", False),
    "SG": ("Senegal", "السنغال", "Africa", False),
    "SH": ("Saint Helena", "سانت هيلينا", "Africa", False),
    "SL": ("Sierra Leone", "سيراليون", "Africa", False),
    "ST": ("Sao Tome and Principe", "ساو تومي وبرينسيبي", "Africa", False),
    "SZ": ("Eswatini", "إسواتيني", "Africa", False),
    "TO": ("Togo", "توغو", "Africa", False),
    "TZ": ("Tanzania", "تنزانيا", "Africa", False),
    "UG": ("Uganda", "أوغندا", "Africa", False),
    "WA": ("Namibia", "ناميبيا", "Africa", False),
    "WI": ("Western Sahara", "الصحراء الغربية", "Africa", False),
    "EH": ("Western Sahara", "الصحراء الغربية", "Africa", False),
    "ZA": ("Zambia", "زامبيا", "Africa", False),
    "ZM": ("Zambia", "زامبيا", "Africa", False),
    "ZI": ("Zimbabwe", "زيمبابوي", "Africa", False),
    "OD": ("South Sudan", "جنوب السودان", "Africa", False),

    # === Asia (قارة آسيا - الدول غير العربية) ===
    "AF": ("Afghanistan", "أفغانستان", "Asia", False),
    "AJ": ("Azerbaijan", "أذربيجان", "Asia", False),
    "AZ": ("Azerbaijan", "أذربيجان", "Asia", False),
    "AM": ("Armenia", "أرمينيا", "Asia", False),
    "BG": ("Bangladesh", "بنغلاديش", "Asia", False),
    "BM": ("Burma (Myanmar)", "ميانمار", "Asia", False),
    "BT": ("Bhutan", "بوتان", "Asia", False),
    "BX": ("Brunei", "بروناي", "Asia", False),
    "CB": ("Cambodia", "كمبوديا", "Asia", False),
    "CH": ("China", "الصين", "Asia", False),
    "GG": ("Georgia", "جورجيا", "Asia", False),
    "GE": ("Georgia", "جورجيا", "Asia", False),
    "HK": ("Hong Kong", "هونغ كونغ", "Asia", False),
    "ID": ("Indonesia", "إندونيسيا", "Asia", False),
    "IN": ("India", "الهند", "Asia", False),
    "IR": ("Iran", "إيران", "Asia", False),
    "JA": ("Japan", "اليابان", "Asia", False),
    "JP": ("Japan", "اليابان", "Asia", False),
    "KG": ("Kyrgyzstan", "قيرغيزستان", "Asia", False),
    "KN": ("North Korea", "كوريا الشمالية", "Asia", False),
    "KS": ("South Korea", "كوريا الجنوبية", "Asia", False),
    "KZ": ("Kazakhstan", "كازاخستان", "Asia", False),
    "LA": ("Laos", "لاوس", "Asia", False),
    "MC": ("Macau", "ماكاو", "Asia", False),
    "MG": ("Mongolia", "منغوليا", "Asia", False),
    "MN": ("Mongolia", "منغوليا", "Asia", False),
    "MY": ("Malaysia", "ماليزيا", "Asia", False),
    "MV": ("Maldives", "المالديف", "Asia", False),
    "NP": ("Nepal", "نيبال", "Asia", False),
    "PK": ("Pakistan", "باكستان", "Asia", False),
    "RP": ("Philippines", "الفلبين", "Asia", False),
    "PH": ("Philippines", "الفلبين", "Asia", False),
    "SN": ("Singapore", "سنغافورة", "Asia", False),
    "CE": ("Sri Lanka", "سريلانكا", "Asia", False),
    "TH": ("Thailand", "تايلاند", "Asia", False),
    "TI": ("Tajikistan", "طاجيكستان", "Asia", False),
    "TJ": ("Tajikistan", "طاجيكستان", "Asia", False),
    "TM": ("Turkmenistan", "تركمانستان", "Asia", False),
    "TX": ("Turkmenistan", "تركمانستان", "Asia", False),
    "TR": ("Turkey", "تركيا", "Asia", False),
    "TU": ("Turkey", "تركيا", "Asia", False),
    "TW": ("Taiwan", "تايوان", "Asia", False),
    "UZ": ("Uzbekistan", "أوزبكستان", "Asia", False),
    "VM": ("Vietnam", "فيتنام", "Asia", False),
    "VN": ("Vietnam", "فيتنام", "Asia", False),
    "TP": ("Timor-Leste", "تيمور الشرقية", "Asia", False),
    "TL": ("Timor-Leste", "تيمور الشرقية", "Asia", False),

    # === Europe (قارة أوروبا) ===
    "AL": ("Albania", "ألبانيا", "Europe", False),
    "AN": ("Andorra", "أندورا", "Europe", False),
    "AU": ("Austria", "النمسا", "Europe", False),
    "AT": ("Austria", "النمسا", "Europe", False),
    "BE": ("Belgium", "بلجيكا", "Europe", False),
    "BK": ("Bosnia and Herzegovina", "البوسنة والهرسك", "Europe", False),
    "BO": ("Belarus", "بيلاروسيا", "Europe", False),
    "BU": ("Bulgaria", "بلغاريا", "Europe", False),
    "CY": ("Cyprus", "قبرص", "Europe", False),
    "DA": ("Denmark", "الدنمارك", "Europe", False),
    "DK": ("Denmark", "الدنمارك", "Europe", False),
    "EI": ("Ireland", "أيرلندا", "Europe", False),
    "IE": ("Ireland", "أيرلندا", "Europe", False),
    "EN": ("Estonia", "إستونيا", "Europe", False),
    "EE": ("Estonia", "إستونيا", "Europe", False),
    "EZ": ("Czech Republic", "جمهورية التشيك", "Europe", False),
    "FI": ("Finland", "فنلندا", "Europe", False),
    "FO": ("Faroe Islands", "جزر فارو", "Europe", False),
    "FR": ("France", "فرنسا", "Europe", False),
    "GI": ("Gibraltar", "جبل طارق", "Europe", False),
    "GM": ("Germany", "ألمانيا", "Europe", False),
    "DE": ("Germany", "ألمانيا", "Europe", False),
    "GR": ("Greece", "اليونان", "Europe", False),
    "HR": ("Croatia", "كرواتيا", "Europe", False),
    "HU": ("Hungary", "المجر", "Europe", False),
    "IC": ("Iceland", "أيسلندا", "Europe", False),
    "IT": ("Italy", "إيطاليا", "Europe", False),
    "LG": ("Latvia", "لاتفيا", "Europe", False),
    "LH": ("Lithuania", "ليتوانيا", "Europe", False),
    "LO": ("Slovakia", "سلوفاكيا", "Europe", False),
    "SK": ("Slovakia", "سلوفاكيا", "Europe", False),
    "LS": ("Liechtenstein", "ليختنشتاين", "Europe", False),
    "LU": ("Luxembourg", "لوكسمبورغ", "Europe", False),
    "MD": ("Moldova", "مولدوفا", "Europe", False),
    "MJ": ("Montenegro", "الجبل الأسود", "Europe", False),
    "MK": ("North Macedonia", "مقدونيا الشمالية", "Europe", False),
    "MT": ("Malta", "مالطا", "Europe", False),
    "NL": ("Netherlands", "هولندا", "Europe", False),
    "NO": ("Norway", "النرويج", "Europe", False),
    "PL": ("Poland", "بولندا", "Europe", False),
    "PO": ("Portugal", "البرتغال", "Europe", False),
    "PT": ("Portugal", "البرتغال", "Europe", False),
    "RO": ("Romania", "رومانيا", "Europe", False),
    "RS": ("Russia", "روسيا الاتحادية", "Europe", False),
    "RU": ("Russia", "روسيا الاتحادية", "Europe", False),
    "SI": ("Slovenia", "سلوفينيا", "Europe", False),
    "SM": ("San Marino", "سان مارينو", "Europe", False),
    "SP": ("Spain", "إسبانيا", "Europe", False),
    "ES": ("Spain", "إسبانيا", "Europe", False),
    "SR": ("Serbia", "صربيا", "Europe", False),
    "SV": ("Svalbard", "سفالبارد", "Europe", False),
    "SW": ("Sweden", "السويد", "Europe", False),
    "UK": ("United Kingdom", "المملكة المتحدة", "Europe", False),
    "UP": ("Ukraine", "أوكرانيا", "Europe", False),
    "UA": ("Ukraine", "أوكرانيا", "Europe", False),
    "VT": ("Vatican City", "الفاتيكان", "Europe", False),
    "XK": ("Kosovo", "كوسوفو", "Europe", False),
    "KV": ("Kosovo", "كوسوفو", "Europe", False),
    "IM": ("Isle of Man", "جزيرة مان", "Europe", False),
    "JE": ("Jersey", "جيرزي", "Europe", False),

    # === North America (أمريكا الشمالية والوسطى والكاريبي) ===
    "AC": ("Antigua and Barbuda", "أنتيغوا وباربودا", "North America", False),
    "BB": ("Barbados", "باربادوس", "North America", False),
    "BD": ("Bermuda", "برمودا", "North America", False),
    "BF": ("Bahamas", "الباهاماس", "North America", False),
    "BS": ("Bahamas", "الباهاماس", "North America", False),
    "BH": ("Belize", "بليز", "North America", False),
    "CA": ("Canada", "كندا", "North America", False),
    "CJ": ("Cayman Islands", "جزر كايمان", "North America", False),
    "KY": ("Cayman Islands", "جزر كايمان", "North America", False),
    "CS": ("Costa Rica", "كوستاريكا", "North America", False),
    "CR": ("Costa Rica", "كوستاريكا", "North America", False),
    "CU": ("Cuba", "كوبا", "North America", False),
    "DO": ("Dominica", "دومينيكا", "North America", False),
    "DR": ("Dominican Republic", "جمهورية الدومينيكان", "North America", False),
    "GL": ("Greenland", "غرينلاند", "North America", False),
    "GP": ("Guadeloupe", "غوادلوب", "North America", False),
    "GT": ("Guatemala", "غواتيمالا", "North America", False),
    "HA": ("Haiti", "هايتي", "North America", False),
    "HT": ("Haiti", "هايتي", "North America", False),
    "HO": ("Honduras", "هندوراس", "North America", False),
    "HN": ("Honduras", "هندوراس", "North America", False),
    "JM": ("Jamaica", "جامايكا", "North America", False),
    "MB": ("Martinique", "مارتينيك", "North America", False),
    "MX": ("Mexico", "المكسيك", "North America", False),
    "NU": ("Nicaragua", "نيكاراغوا", "North America", False),
    "PM": ("Panama", "بنما", "North America", False),
    "RN": ("Saint Martin", "سان مارتان", "North America", False),
    "SB": ("Saint Pierre and Miquelon", "سان بيير وميكلون", "North America", False),
    "SC": ("Saint Kitts and Nevis", "سانت كيتس ونيفيس", "North America", False),
    "ST": ("Saint Lucia", "سانت لوسيا", "North America", False),
    "TD": ("Trinidad and Tobago", "ترينيداد وتوباغو", "North America", False),
    "TT": ("Trinidad and Tobago", "ترينيداد وتوباغو", "North America", False),
    "TK": ("Turks and Caicos Islands", "جزر تركس وكايكوس", "North America", False),
    "US": ("United States", "الولايات المتحدة الأمريكية", "North America", False),
    "VC": ("Saint Vincent and Grenadines", "سانت فينسنت والغرينادين", "North America", False),
    "VI": ("Virgin Islands (US)", "الجزر العذراء الأمريكية", "North America", False),
    "VQ": ("Virgin Islands (US)", "الجزر العذراء الأمريكية", "North America", False),
    "AA": ("Aruba", "أروبا", "North America", False),
    "CW": ("Curacao", "كوراساو", "North America", False),
    "GJ": ("Grenada", "غرينادا", "North America", False),
    "NT": ("Netherlands Antilles", "جزر الأنتيل الهولندية", "North America", False),

    # === South America (أمريكا الجنوبية) ===
    "AR": ("Argentina", "الأرجنتين", "South America", False),
    "BL": ("Bolivia", "بوليفيا", "South America", False),
    "BR": ("Brazil", "البرازيل", "South America", False),
    "CI": ("Chile", "تشيلي", "South America", False),
    "CL": ("Chile", "تشيلي", "South America", False),
    "CO": ("Colombia", "كولومبيا", "South America", False),
    "EC": ("Ecuador", "الإكوادور", "South America", False),
    "FG": ("French Guiana", "غويانا الفرنسية", "South America", False),
    "GF": ("French Guiana", "غويانا الفرنسية", "South America", False),
    "GY": ("Guyana", "غيانا", "South America", False),
    "PA": ("Paraguay", "باراغواي", "South America", False),
    "PY": ("Paraguay", "باراغواي", "South America", False),
    "PE": ("Peru", "بيرو", "South America", False),
    "NS": ("Suriname", "سورينام", "South America", False),
    "UY": ("Uruguay", "أوروغواي", "South America", False),
    "VE": ("Venezuela", "فنزويلا", "South America", False),
    "FK": ("Falkland Islands", "جزر فوكلاند", "South America", False),

    # === Oceania (أوقيانوسيا وأستراليا وجزر المحيط الهادئ) ===
    "AS": ("Australia", "أستراليا", "Oceania", False),
    "AQ": ("American Samoa", "ساموا الأمريكية", "Oceania", False),
    "BP": ("Solomon Islands", "جزر سليمان", "Oceania", False),
    "CK": ("Cocos (Keeling) Islands", "جزر كوكوس", "Oceania", False),
    "CC": ("Cocos (Keeling) Islands", "جزر كوكوس", "Oceania", False),
    "CR": ("Coral Sea Islands", "جزر بحر المرجان", "Oceania", False),
    "FJ": ("Fiji", "فيجي", "Oceania", False),
    "FM": ("Micronesia", "ميكرونيزيا", "Oceania", False),
    "FP": ("French Polynesia", "بولينيزيا الفرنسية", "Oceania", False),
    "PF": ("French Polynesia", "بولينيزيا الفرنسية", "Oceania", False),
    "GQ": ("Guam", "غوام", "Oceania", False),
    "GU": ("Guam", "غوام", "Oceania", False),
    "KR": ("Kiribati", "كيريباتي", "Oceania", False),
    "MH": ("Marshall Islands", "جزر مارشال", "Oceania", False),
    "RM": ("Marshall Islands", "جزر مارشال", "Oceania", False),
    "NC": ("New Caledonia", "كاليدونيا الجديدة", "Oceania", False),
    "NF": ("Norfolk Island", "جزيرة نورفولك", "Oceania", False),
    "NH": ("Vanuatu", "فانواتو", "Oceania", False),
    "NR": ("Nauru", "ناورو", "Oceania", False),
    "NZ": ("New Zealand", "نيوزيلندا", "Oceania", False),
    "PC": ("Pitcairn Islands", "جزر بيتكيرن", "Oceania", False),
    "PN": ("Pitcairn Islands", "جزر بيتكيرن", "Oceania", False),
    "PP": ("Papua New Guinea", "بابوا غينيا الجديدة", "Oceania", False),
    "PW": ("Palau", "بالاو", "Oceania", False),
    "TN": ("Tonga", "تونغا", "Oceania", False),
    "TV": ("Tuvalu", "توفالو", "Oceania", False),
    "WF": ("Wallis and Futuna", "واليس وفوتونا", "Oceania", False),
    "WS": ("Samoa", "ساموا", "Oceania", False),
    "CQ": ("Northern Mariana Islands", "جزر ماريانا الشمالية", "Oceania", False),
    "TL": ("Tokelau", "توكيلاو", "Oceania", False),
    "TK": ("Tokelau", "توكيلاو", "Oceania", False),
    "KT": ("Christmas Island", "جزيرة كريسماس", "Oceania", False),
    "NE": ("Niue", "نييوي", "Oceania", False),
    "AI": ("Anguilla", "أنغويلا", "North America", False),

    # === Antarctica & Polar (القطب الجنوبي والجزر النائية) ===
    "AY": ("Antarctica", "القارة القطبية الجنوبية (أنتاركتيكا)", "Antarctica", False),
    "BV": ("Bouvet Island", "جزيرة بوفيه", "Antarctica", False),
    "HM": ("Heard and McDonald Islands", "جزيرة هيرد وجزر ماكدونالد", "Antarctica", False),
    "FS": ("French Southern Territories", "الأقاليم الجنوبية الفرنسية", "Antarctica", False),
    "SX": ("South Georgia", "جورجيا الجنوبية", "Antarctica", False),
    # === Added African Territories & Countries ===
    "JU": ("Juan de Nova Island", "جزيرة جوان دي نوفا", "Africa", False),
    "EU": ("Europa Island", "جزيرة يوروبا", "Africa", False),
    "TE": ("Tromelin Island", "جزيرة تروملين", "Africa", False),
    "RE": ("Reunion", "لا ريونيون", "Africa", False),
    "WZ": ("Eswatini (Swaziland)", "إسواتيني", "Africa", False),
    "MF": ("Mayotte", "مايوت", "Africa", False),
    "UV": ("Burkina Faso", "بوركينا فاسو", "Africa", False),

    # === Added European Territories ===
    "RI": ("Serbia", "صربيا", "Europe", False),

    # === Added North American & Caribbean Territories ===
    "UC": ("Curacao", "كوراساو", "North America", False),
    "AV": ("Anguilla", "أنغويلا", "North America", False),
    "RQ": ("Puerto Rico", "بورتوريكو", "North America", False),
    "NN": ("Sint Maarten", "سينت مارتن", "North America", False),

    # === Added Oceania & Pacific Atolls ===
    "LQ": ("Palmyra Atoll", "جزيرة بالميرا المرجانية", "Oceania", False),
    "CT": ("Canton and Enderbury Islands", "جزر كانتون", "Oceania", False),
    "JQ": ("Johnston Atoll", "جزيرة جونستون", "Oceania", False),
    "MQ": ("Midway Islands", "جزر ميدواي", "Oceania", False),
    "WQ": ("Wake Island", "جزيرة ويك", "Oceania", False),

    # === Added Indian Ocean Territory ===
    "IO": ("British Indian Ocean Territory", "إقليم المحيط الهندي البريطاني", "Asia", False),

    # === Additional Islands ===
    "CP": ("Clipperton Island", "جزيرة كليبرتون", "North America", False),
    "DQ": ("Jarvis Island", "جزيرة جارفيس", "Oceania", False),
    "FQ": ("Baker Island", "جزيرة بيكر", "Oceania", False),

    # === International Waters & Marine Buoys ===
    "INT": ("International Waters / Marine Buoys", "المياه الدولية وعوامات الرصد البحرية", "Oceans", False),
    "nan": ("International Waters / Marine Buoys", "المياه الدولية وعوامات الرصد البحرية", "Oceans", False),
    "": ("International Waters / Marine Buoys", "المياه الدولية وعوامات الرصد البحرية", "Oceans", False),
}

def get_country_info(code, lat=None, lon=None):
    """Retrieve (en_name, ar_name, continent, is_arab) for code, with sovereign normalization and spatial disambiguation."""
    if not code or str(code).strip() in ("", "nan", "None"):
        return ("International Waters / Marine Buoys", "المياه الدولية وعوامات الرصد البحرية", "Oceans", False)
    code_up = str(code).strip().upper()
    
    # 1. Sovereign Unification & Palestine vs Europe/Pacific
    if code_up in ("IS", "IL", "GZ", "WE", "PS"):
        # Check if coordinates belong to Palau in the Pacific (lat ~7, lon ~134)
        if lat is not None and lon is not None and (lat < 15.0 and lon > 100.0):
            return ("Palau", "بالاو", "Oceania", False)
        # Check if bogus test station in Europe (e.g. Germany lat ~52, lon ~7)
        if lat is not None and lon is not None and (lat > 40.0 or lon < 20.0):
            return ("Germany", "ألمانيا", "Europe", False)
        return ("Palestine", "دولة فلسطين", "Asia", True)

    # 2. Comoros (KM / CN) vs China (CN / CH)
    if code_up in ("CN", "KM"):
        # Comoros is in the Mozambique Channel: Lat approx -11.0 to -13.5, Lon 43.0 to 45.5
        if lat is not None and lon is not None:
            if (-20.0 < lat < -5.0) and (40.0 < lon < 50.0):
                return ("Comoros", "جمهورية جزر القمر الاتحادية", "Africa", True)
            else:
                return ("China", "جمهورية الصين الشعبية", "Asia", False)
        # Default fallback if coordinates missing (FIPS CN in Arab League registry is Comoros)
        return ("Comoros", "جمهورية جزر القمر الاتحادية", "Africa", True)

    # 3. Bahrain (BA / BH) vs Bosnia (BA / BK) vs Belize (BH)
    if code_up in ("BA", "BH"):
        # Belize is in Central America: Lon < 0 (approx -87 to -89)
        if lon is not None and lon < 0:
            return ("Belize", "بليز", "North America", False)
        # Bosnia & Herzegovina is in SE Europe: Lat > 35
        if lat is not None and lat > 35.0:
            return ("Bosnia and Herzegovina", "البوسنة والهرسك", "Europe", False)
        # Bahrain is in the Persian Gulf: Lat ~ 25.5 to 26.5, Lon ~ 50.0 to 51.0
        if lat is not None and lon is not None:
            if (24.0 < lat < 28.0) and (49.0 < lon < 52.0):
                return ("Bahrain", "مملكة البحرين", "Asia", True)
        if code_up == "BA":
            return ("Bahrain", "مملكة البحرين", "Asia", True)
        return ("Belize", "بليز", "North America", False)

    # 4. Iraq (IZ / IQ) test stations in Europe
    if code_up in ("IZ", "IQ"):
        if lat is not None and lat > 45.0:
            return ("Germany", "ألمانيا", "Europe", False)
        return ("Iraq", "جمهورية العراق", "Asia", True)

    if code_up in COUNTRY_REGISTRY:
        return COUNTRY_REGISTRY[code_up]
    return (code_up, code_up, "Other", False)
