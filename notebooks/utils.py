import gepadeu
import json
import sys    
import re


"""
Takes a document id and returns the whole speech.
"""
def speech_by_docid(content_dic, doc_id):
    return content_dic[doc_id]

def party_by_docid(meta_dic, doc_id):
    return meta_dic[doc_id]['party']

def speaker_by_docid(meta_dic, doc_id):
    return meta_dic[doc_id]['speaker']

def speechid_by_docid(meta_dic, doc_id):
    return meta_dic[doc_id]['speech_id']

def date_by_docid(meta_dic, doc_id):
    return meta_dic[doc_id]['date']

def year_by_docid(meta_dic, doc_id):
    return meta_dic[doc_id]['year']

def term_by_docid(meta_dic, doc_id):
    return meta_dic[doc_id]['term']

def session_by_docid(meta_dic, doc_id):
    return meta_dic[doc_id]['session']

def source_by_docid(meta_dic, doc_id):
    return meta_dic[doc_id]['source'] 

def function_by_docid(meta_dic, doc_id):

    return meta_dic[doc_id]['source'] 


# TODO: check party names for older legislative terms (LINKE, PDS?)
def is_gov_opp(party, term):
    if party == 'fraktionslos':
        return 'fraktionslos'
    legislative = {
        21: {
            'AfD': 'opp',
            'CDU_CSU': 'gov',
            'GRUENE': 'opp',
            'LINKE': 'opp',
            'SPD': 'gov',
            'SSIW': 'opp'
            },
        20: {
            'AfD': 'opp',
            'CDU_CSU': 'opp',
            'FDP': 'gov',
            'GRUENE': 'gov',
            'LINKE': 'opp',
            'SPD': 'gov',
            'SSIW': 'opp'
        },
        19: {
            'AfD': 'opp',
            'CDU_CSU': 'gov',
            'FDP': 'opp',
            'GRUENE': 'opp',
            'LINKE': 'opp',
            'SPD': 'gov'
        },
        18: { 
            'CDU_CSU': 'gov', 
            'GRUENE': 'opp',
            'LINKE': 'opp',
            'SPD': 'gov'
        },
        17: {
            'CDU_CSU': 'gov',
            'FDP': 'gov',
            'GRUENE': 'opp',
            'LINKE': 'opp',
            'SPD': 'opp'
        },
        16: {
            'CDU_CSU': 'gov',
            'FDP': 'opp',
            'GRUENE': 'opp',
            'LINKE': 'opp',
            'SPD': 'gov'
        },
        15: {
            'CDU_CSU': 'opp',
            'FDP': 'opp',
            'GRUENE': 'gov',
            'LINKE': 'opp',
            'PDS': 'opp',
            'SPD': 'gov'
        },
        14: {
            'CDU_CSU': 'opp',
            'FDP': 'opp',
            'GRUENE': 'gov',
            'LINKE': 'opp',
            'PDS': 'opp',
            'SPD': 'gov'
        },
        13: {
            'CDU_CSU': 'gov',
            'FDP': 'gov',
            'GRUENE': 'opp',
            'LINKE': 'opp',
            'PDS': 'opp',
            'SPD': 'opp'
        },
        12: {
            'CDU_CSU': 'gov',
            'FDP': 'gov',
            'GRUENE': 'opp',
            'LINKE': 'opp',
            'PDS': 'opp',
            'SPD': 'opp'
        },
        11: {
            'CDU_CSU': 'gov',
            'FDP': 'gov',
            'GRUENE': 'opp',
            'SPD': 'opp'
        },
        10: {
            'CDU_CSU': 'gov',
            'FDP': 'gov',
            'GRUENE': 'opp', 
            'SPD': 'opp'
        },
        9: {
            'CDU_CSU': 'gov',
            'FDP': 'gov', 
            'SPD': 'opp'
        },
        8: {
            'CDU_CSU': 'opp',
            'FDP': 'gov', 
            'SPD': 'gov'
        },
        7: {
            'CDU_CSU': 'opp',
            'FDP': 'gov', 
            'SPD': 'gov'
        },
        6: {
            'CDU_CSU': 'opp',
            'FDP': 'gov', 
            'SPD': 'gov'
        },
        5: { 
            # FIXME: Koalitionsbruch?
        },
        4: {
            'CDU_CSU': 'gov',
            'FDP': 'gov', 
            'SPD': 'opp'
        },
        3: { 
            'CDU_CSU': 'gov',
            'DP': 'gov',
            'FDP': 'opp',
            'FDV': 'opp', 
            'SPD': 'opp'
        },
        2: { 
            'CDU_CSU': 'gov',
            'BHE': 'gov',
            'DP': 'gov',
            'DZP': 'opp',
            'FDP': 'gov', 
            'SPD': 'opp'
        },
        1: { 
            'CDU_CSU': 'gov',
            'BP': 'opp',
            'DKP-DRP': 'opp',
            'DP': 'gov',
            'DZP': 'opp',
            'FDP': 'gov',
            'KPD': 'opp', 
            'SPD': 'opp',
            'SSIW': 'opp',
            'Unabhängige': 'opp',
            'WAV': 'opp'
        }
    }
    return legislative[term][party]



def get_parties():
    return ['AfD', 'CDU_CSU', 'FDP', 'GRUENE', 'LINKE', 'SPD', 'fraktionslos']

def get_speechact_labels():
    return ['Accusation', 'Bad-outcome', 'Demand', 'Evaluation', 'Expressive', 'I-S-Humour', 'Macro', 'Question-All', 'Promise', 'Rejection', 'Report', 'Request', 'Self-representation', 'Support']

def get_mf_labels():
    return ['Authority', 'Care', 'Equality', 'Liberty', 'Loyalty', 'Proportionality', 'Purity', 'General-Moral', 'PoliticalActOrGoal']

def get_spkatt_role_labels():
    return ['Addr', 'Source', 'Message', 'Topic', 'Medium', 'Evidence']

def get_mope_labels():
    return ['eoFinanz', 'eoMedia', 'eoMil', 'eoMov', 'eoNgo', 'eoPol', 'eoRel', 'eoSci', 'eoWirt', 'epFinanz', 'epKult', 'epMedia', 'epMil', 'epMov', 'epNgo', 'epOwn', 'epPol', 'epRel', 'epSci', 'epWirt', 'GPE', 'pAge', 'pEth', 'pFunk', 'pGen', 'pNat', 'pSoz']

def get_mope_mapping():
    return {
        'EOFINANZ': 'eoFinanz', 
        'EOMEDIA': 'eoMedia', 
        'EOMIL': 'eoMil', 
        'EOMOV': 'eoMov', 
        'EONGO': 'eoNgo', 
        'EOPOL': 'eoPol', 
        'EOREL': 'eoRel', 
        'EOSCI': 'eoSci', 
        'EOWIRT': 'eoWirt', 
        'EPFINANZ': 'epFinanz',
        'EPKULT': 'epKult',
        'EPMEDIA': 'epMedia', 
        'EPMIL': 'epMil', 
        'EPMOV': 'epMov', 
        'EPNGO': 'epNgo', 
        'EPOWN': 'epOwn', 
        'EPPOL': 'epPol', 
        'EPREL': 'epRel', 
        'EPSCI': 'epSci', 
        'EPWIRT': 'epWirt', 
        'GPE': 'GPE', 
        'PAGE': 'pAge', 
        'PETH': 'pEth', 
        'PFUNK': 'pFunk', 
        'PGEN': 'pGen', 
        'PNAT': 'pNat', 
        'PSOZ': 'pSoz'
    }


    
def get_sitent_labels():
    return ['STATE', 'EVENT', 'REPORT', 'GENERIC', 'GENERALIZING', 'FACT', 'PROPOSITION', 'EVENT-PERFECT-STATE', 'IMPERATIVE', 'QUESTION']
    

# check if two lists (indicated by their start and end indices)
# do overlap
def span_overlap(s1, e1, s2, e2): 
    if not set([x for x in range(s1, e1+1)]).isdisjoint([x for x in range(s2, e2+1)]):
        return True
    return False


"""
Takes a list of keywords and extracts speeches that have
at least 3 keyword matches (same or different keywords) 
"""
def filter_speeches_by_keywords(speeches, keyword_list, strict_match, ignore_case):
    filtered_speeches = []
    pattern_str, pattern = None, None
    if strict_match:
        # exact word match (pay attention to word boundaries)
        pattern_str = '\\b(?:'+ '|'.join(keyword_list) +')\\b'
    else:
        # any match
        pattern_str = '(?:'+ '|'.join(keyword_list) +')'
    if ignore_case:
        pattern = re.compile(pattern_str, re.IGNORECASE)
    else:
        pattern = re.compile(pattern_str, re.IGNORECASE)

    for speech in speeches:
        if len(re.findall(pattern, " ".join(speech.words))) > 2:
            filtered_speeches.append(speech)
    return filtered_speeches


"""
Specifies the colors used for visualisation
for the different labels.
"""
def get_colors():
    return {
            "Accusation": "#661100",
            "Bad Outcome": "#332288",
            "Expressive": "#999933",
            "Macro": "#DDCC77",
            "Rejection": "#882255",            
            "Report": "#88CCEE",            
            "Request": "#44AA99",
            "Support": "#117733",
            "Promise": "#8E6278",
            "Demand": "#AA4499",
            "Request": "#aa9cfc",
            "Question-All": "#006DDB",
            "Report": "#f99cfc",
            "Accusation": "#f99cfc",
            "Evaluation": "#888888",
            "Self-representation": "#A96357", 
            "Care": "#661100",
            "Equality": "#DDCC77",
            "Proportionality": "#999933",
            "Loyalty": "#DDCC77",
            "Authority": "#882255",            
            "Purity": "#88CCEE",            
            "Liberty": "#44AA99",
            "General-Moral": "#117733",
        }


"""
Takes a list of Gepadeu objects and sorts them by party.
Returns a dictionary with parties as keys.
"""
def sort_speeches_by_party(speeches):
    parties = get_parties()
    party_dict = {p:[] for p in parties}

    for speech in speeches:
        party_dict[speech.party].append(speech)

    return party_dict


"""
Takes an annotation dictionary and sorts the annotations by party affiliation.
Returns a dictionary with parties as keys.
"""
def sort_annots_by_party(annot_dict, meta_dict):
    parties = ['AfD', 'CDU_CSU', 'FDP', 'GRUENE', 'LINKE', 'SPD', 'fraktionslos']
    party_dict = {p:{} for p in parties}

    for doc_id in annot_dict:
        for label in annot_dict[doc_id]:
            if label not in party_dict[meta_dict[doc_id]['party']]:
                party_dict[meta_dict[doc_id]['party']][label] = []
            if annot_dict[doc_id][label] == []:
                continue
            for dic in annot_dict[doc_id][label]:
                party_dict[meta_dict[doc_id]['party']][label].append(dic) 
    return party_dict


"""
Takes a list of Gepadeu objects and sorts them by legislative term.
Returns a dictionary with term as keys.
"""
def sort_speeches_by_term(speeches):
    terms = list(set([speech.term for speech in speeches]))
    term_dict = {t:[] for t in terms}

    for speech in speeches:
        term_dict[speech.term].append(speech)

    return term_dict


"""
Takes a list of Gepadeu objects and sorts them by year.
Returns a dictionary with year as keys.
"""
def sort_speeches_by_year(speeches):
    years = list(set([speech.year for speech in speeches]))
    year_dict = {y:[] for y in years}

    for speech in speeches:
        year_dict[speech.year].append(speech)
    return year_dict


"""
Takes a list of speeches (Gepadeu objects) and extracts the content tokens for each speech.
Returns a dictionary with doc_ids as keys and the content for each key.
"""
def extract_content(speeches):
    content_dict = {}
    for speech in speeches:
        content_dict[speech.doc_id] = speech.words
    return content_dict


"""
Takes a list of speeches (Gepadeu objects) and extracts the metadata for each speech.
Returns a dictionary with doc_ids as keys and the metadata for each key.
"""
def extract_metadata(speeches):
    meta_dict = {}
    for speech in speeches:
        meta_dict[speech.doc_id] = {
            'doc_id': speech.doc_id,
            'speech_id': speech.speech_id,
            'party': speech.party,
            'date': speech.date,
            'year': speech.year,
            'speaker': speech.speaker,
            'term': speech.term,
            'session': speech.session,
            'gov_opp': speech.gov_opp,
            'source': speech.source
        }
    return meta_dict


"""
Attention: this is only an approximation when applied to large data as there might be more than one politician with the same last name affiliated with the same party.
"""
def get_number_of_speakers(speeches):
    speakers = []
    for speech in speeches:
        speakers.append(speech.speaker + '_' + speech.party)
    return len(list(set(speakers)))

def get_number_of_parties(speeches):
    parties = [speech.party for speech in speeches]
    return len(list(set(parties)))


def get_number_of_speechacts(speeches):
    speechacts = 0
    speechact_dict = extract_speechacts(speeches)  
    # count number of speechacts 
    for doc_id in speechact_dict: 
        for label in speechact_dict[doc_id]:
            speechacts += len(speechact_dict[doc_id][label])
    return speechacts

# TODO
def get_number_of_spkatt_triggers(speeches):
    return

# TODO
def get_number_of_spkatt_roles(speeches):
    return

# TODO
def get_number_of_moral_frames(speeches):
    return

# TODO
def get_number_of_moral_roles(speeches):
    return

# TODO
def get_number_of_sitents(speeches):
    return

# TODO
def get_number_of_mope_entities(speeches):
    return

# TODO
def get_number_of_named_entities(speeches):
    return

def get_speech_by_docid(speeches, doc_id):
    for speech in speeches:
        if speech.doc_id == doc_id:
            return speech
    return


def get_speeches_per_party(speeches, parties):
    stats_dict = {p:0 for p in parties}
    for speech in speeches:
        stats_dict[speech.party] += 1
    return stats_dict


def get_speeches_per_year(speeches):
    years = list(set([speech.year for speech in speeches]))
    stats_dict = {y:0 for y in years}
    for speech in speeches:
        stats_dict[speech.year] += 1
    return stats_dict


def get_speeches_per_term(speeches):
    terms = list(set([speech.term for speech in speeches]))
    stats_dict = {t:0 for t in terms}
    for speech in speeches:
        stats_dict[speech.term] += 1
    return stats_dict


"""
Takes a dictionary with annotations for a keyword and prints the number of annotations for layer 'layer' for each party and label on this annotation layer.
annot_dict format:
{
    '19040_Zusatzpunkt_9_AfD_Herrmann_ID194007600_15.06.2018': {}, 
    '19150_Tagesordnungspunkt_23_GRUENE_Doerner_ID1915000800_06.03.2020': 
        {'SPEECHACT': {'Self-representation': 1}, 'MORAL': {'Equality': 1}},
    ...
}
"""
def keyword_per_party(keyword, annot_dict, meta_dict, layer):
    parties = ['AfD', 'CDU_CSU', 'FDP', 'GRUENE', 'LINKE', 'SPD', 'fraktionslos']
    stats = {party:{} for party in parties}

    for doc_id, annots in annot_dict.items():
        party = meta_dict[doc_id]['party']
        if layer not in annots:
            continue
        for label, freq in annots[layer].items():
            if label not in stats[party]: stats[party][label] = 0
            stats[party][label] += freq

    print("KEYWORD:", keyword, "\tLAYER:", layer)
    for party in stats:
        for label in stats[party]:
            print(party, "\t", label, "\t", stats[party][label])
    return



"""
Takes a list of speeches (Gepadeu objects) and extracts some corpus statistics:
- no. speeches
- no. speakers
- no. parties
- no. speeches per party
- no. speeches per year
- no. speeches per term
- no. speechacts per party
- no. moral frames (by MF) per party
- no. sitent per party # TODO
- no. spkatt roles per party # TODO


Returns a dictionary with doc_ids as keys and the metadata for each key.
"""
def extract_stats(speeches):
    parties = ['AfD', 'CDU_CSU', 'FDP', 'GRUENE', 'LINKE', 'SPD', 'fraktionslos']
    meta_dict = extract_metadata(speeches)

    stats_dict = {
        'speeches': len(speeches),
        'speakers': get_number_of_speakers(speeches),
        'parties': get_number_of_parties(speeches),
        'speechacts': get_number_of_speechacts(speeches),
        'spkatt_trigger': get_number_of_spkatt_roles(speeches),
        'spkatt_roles': get_number_of_spkatt_roles(speeches),
        'moral': get_number_of_moral_frames(speeches), 
        'speeches_per_party': get_speeches_per_party(speeches, parties),
        'speeches_per_year': get_speeches_per_year(speeches),
        'speeches_per_term': get_speeches_per_term(speeches),
        #'sitent_per_party':  get_sitent_per_party(speeches, parties, meta_dict), 
        'speechacts_per_party': get_speechacts_per_party(speeches, parties, meta_dict),  
        'mope_mentions_per_party': get_mope_per_party(speeches, parties, meta_dict),  
        'moral_frames_per_party': get_moral_frames_per_party(speeches, parties, meta_dict),
        'spkatt_roles_per_party': get_spkatt_roles_per_party(speeches, parties, meta_dict)
    } 
    return stats_dict


"""
Takes a list of speeches (Gepadeu objects) and extracts all speechacts.
Returns a dictionary with doc_ids as keys, sorted by speechact type for each doc.
"""
def extract_speechacts(speeches):
    speechacts = get_speechact_labels()
    speechact_dict = {}
    for speech in speeches:
        speechact_dict[speech.doc_id] = {speechact:[] for speechact in speechacts} 

        for speechact_id, speechact in speech.speechact.items():
            for label in speechact['labels']:
                tmp = {
                    'start': speechact['start'],
                    'end': speechact['end'],
                    'words': speech.words[speechact['start']:speechact['end']+1] 
                }
                speechact_dict[speech.doc_id][label].append(tmp)
    return speechact_dict



def extract_sitent(speeches):
    sitents = get_sitent_labels()
    sitent_dict = {}
    for speech in speeches:
        sitent_dict[speech.doc_id] = {sitent:[] for sitent in sitents} 
        print(speech.sitent)
        for sitent_id, sitent in speech.sitent.items():
            print(speech.doc_id)
            print(sitent)
            labels = [sitent['label_A1'], sitent['label_A2']]
            print(labels)
            print(len(speech.words))
            print(sitent['token_id'])
            for label in labels:
                tmp = {
                    'id': sitent['token_id'],
                    'words': speech.words[sitent['token_id']] 
                }
                sitent_dict[speech.doc_id][label].append(tmp)

    return sitent_dict




def get_sitent_per_party(speeches, parties, meta_dict):
    sitent_dict = extract_sitent(speeches)
    # get list of situation entities
    sitent = list(set([l for docid in sitent_dict for l in sitent_dict[docid]]))
    stats_dict = {party:{label:0 for label in sitent} for party in parties}
    # count number of speechacts per party
    for doc_id in sitent_dict: 
        for label in sitent_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][label] += len(sitent_dict[doc_id][label])
    return stats_dict




def get_speechacts_per_party(speeches, parties, meta_dict):
    speechact_dict = extract_speechacts(speeches)
    # get list of speechacts
    speechacts = list(set([l for docid in speechact_dict for l in speechact_dict[docid]]))
    stats_dict = {party:{label:0 for label in speechacts} for party in parties}
    # count number of speechacts per party
    for doc_id in speechact_dict: 
        for label in speechact_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][label] += len(speechact_dict[doc_id][label])
    return stats_dict




def get_mope_per_party(speeches, parties, meta_dict):
    mope_dict = extract_mope(speeches) 
    # get list of mope 
    mope = list(set([l for docid in mope_dict for l in mope_dict[docid]]))
    stats_dict = {party:{label:0 for label in mope} for party in parties}
    # count number of speechacts per party
    for doc_id in mope_dict: 
        for label in mope_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][label] += len(mope_dict[doc_id][label])
    return stats_dict



def get_moral_frames_per_party(speeches, parties, meta_dict):
    moral_dict = extract_moral_frames(speeches)
    # get list of moral foundations
    mfs = list(set([mf for docid in moral_dict for mf in moral_dict[docid]])) 
    stats_dict = {party:{mf:0 for mf in mfs} for party in parties} 
    # count number of moral frames per party, for each moral foundation
    for doc_id in moral_dict: 
        for mf in moral_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][mf] += len(moral_dict[doc_id][mf])

    return stats_dict



def get_spkatt_roles_per_party(speeches, parties, meta_dict):
    spkatt_dict = extract_spkatt(speeches) 

    # get list of spkatt roles
    roles = list(set([role for docid in spkatt_dict for role in spkatt_dict[docid]])) 

    stats_dict = {party:{role:0 for role in roles} for party in parties} 
    # count number of moral frames per party, for each moral foundation
    for doc_id in spkatt_dict: 
        for role in spkatt_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][role] += len(spkatt_dict[doc_id][role])

    return stats_dict




"""
Takes a list of speeches (Gepadeu objects) and extracts all named entities (NE).
Returns a dictionary with doc_ids as keys, with NE types for each doc.
TODO: needs to be tested!
"""
def extract_ner(speeches):
    ner_tags = ['AGE', 'ART', 'CARDINAL', 'DATE', 'DUR', 'EVT', 'FAC', 'FRAC', 'FREQ', 'GPE', 'LAN', 'LAW', 'LOC', 'MED', 'MISC', 'MON', 'NRP', 'ORDINAL', 'ORG', 'PER', 'PERC', 'PRODUCT', 'PROJ', 'QUANT', 'RATE', 'SCORE', 'SORD', 'TIME', 'TITLE', 'URL']
    ner_dict = {}
    
    for speech in speeches:
        ner_dict[speech.doc_id] = {}
        for i in range(len(speech.ner)):
            if speech.ner[i] in ner_tags:
                this_annot = {'start':0, 'end':0}
                if i > 0 and speech.ner[i-1] != speech.ner[i]:
                    this_annot['start'] = i
                for j in range(i+1, len(speech.ner)): 
                     
                    if speech.ner[j] != speech.ner[j-i]:
                        this_annot['end'] = j-1
                        this_annot['words'] = speech.words[i:j-1]
                        ner_dict[speech.doc_id][speech.ner[i]] = this_annot

    return ner_dict


"""
Takes a list of speeches (Gepadeu objects) and extracts all moral frames.
Returns a dictionary with doc_ids as keys, sorted by the mf of the moral frame.
"""
def extract_moral_frames(speeches):
    mfs = get_mf_labels()
    moral_dict = {}
    for speech in speeches:
        moral_dict[speech.doc_id] = {mf:[] for mf in mfs}  
        for mdic in speech.moral:
            frame_type = mdic['predicate']
            mf_vote = mdic['MF_majority']
            frame_span = mdic['Frame'] 
            words = speech.words[frame_span[0]-1:frame_span[-1]]
            for mf in mf_vote:
                moral_dict[speech.doc_id][mf].append({'start': frame_span[0]-1, 'end': frame_span[-1], 'words': words}) 
        
    return moral_dict

"""
Takes a list of speeches (Gepadeu objects) and extracts all mentions to
The People and to The Elite (MOPE).
Returns a dictionary with doc_ids as keys, with mope types for each doc.
"""
def extract_mope(speeches):
    mope_tags = get_mope_labels()
    mope_mapping = get_mope_mapping()
    mope_dict = {}
    for speech in speeches:  
        mope_dict[speech.doc_id] = {mope_tag:[] for mope_tag in mope_tags} 
        for i in range(len(speech.mope)):
            if speech.mope[i] == 'O':
                continue
            tag = speech.mope[i].replace('B-', '').replace('I-', '')
            if mope_mapping[tag] in mope_tags:
                this_annot = {'start':0, 'end':0}
                if speech.mope[i].startswith('B-'):
                    this_annot['start'] = i
                    for j in range(i+1, len(speech.mope)): 
                        if speech.mope[j] != 'I-' + tag:
                            this_annot['end'] = j-1
                            this_annot['words'] = speech.words[i:j]
                            mope_dict[speech.doc_id][mope_mapping   [tag]].append(this_annot) 
                            break

    return mope_dict




"""
Takes a list of speeches (Gepadeu objects) and extracts all speaker attribution roles (Source, Addressee, Message, Topic, Medium, Evidence).
Returns a dictionary with doc_ids as keys and the annotations for each role of the speech/thought/writing trigger.
"""
def extract_spkatt(speeches):
    debug = False
    triggers = ['B-V', 'I-V', 'B-PTC', 'I-PTC']
    spkatt_roles = get_spkatt_role_labels()
    spkatt_dict = {}
    unit_dict   = {}
    for speech in speeches:
        spkatt_dict[speech.doc_id] = {r:[] for r in spkatt_roles}  
        unit_dict[speech.doc_id]   = {}
        if debug: print("SPKATT", speech.spkatt)
        if debug: print("SPKATT units", speech.spkatt_units)

        # get spkatt units
        for udx, spkatt_unit in speech.spkatt_units.items():
            unit_dict[speech.doc_id][udx] = {
                'start': spkatt_unit['start'],
                'end': spkatt_unit['end'],
                'span': speech.words[spkatt_unit['start']:spkatt_unit['end']+1]
            }
        if debug: print("UNITS", unit_dict)

        for idx, spkatt in speech.spkatt.items():
            unit = unit_dict[speech.doc_id][idx]['span']
            if debug: print("\nUNIT", unit)
            if debug: print("\nROLES", spkatt["roles"])
            for i in range(len(spkatt["roles"])):
                if spkatt["roles"][i] == '_': continue
                if debug: print("=>", i, spkatt["roles"][i], unit[i])
                prefix, role = spkatt["roles"][i].split('-')
                if role in spkatt_roles: 
                    if prefix == 'B':
                        this_annot = {'start': i, 'end': 0}
                        # last token of role
                        if not spkatt["roles"][i+1].endswith(role):
                            this_annot['end'] = i
                            if debug: print("a start", this_annot['start'], 'end', this_annot['end'])
                            this_annot['words'] = unit[this_annot['start']:this_annot['end']+1]
                            spkatt_dict[speech.doc_id][role].append(this_annot)
                    elif prefix == 'I':
                        if i+1 == len(spkatt["roles"]):
                            break
                        if not spkatt["roles"][i+1].endswith(role):
                            this_annot['end'] = i
                            if debug: print("b start", this_annot['start'], 'end', this_annot['end'])
                            this_annot['words'] = unit[this_annot['start']:this_annot['end']+1]
                            spkatt_dict[speech.doc_id][role].append(this_annot)

    return spkatt_dict

"""
Takes a token string and returns all token ids for this token
as a list.
"""
def search_for(speeches, keyword):
    token_ids = {}; num_instances = 0
    for speech in speeches:
        #TODO: nur token match erlauben, keine subtokens!!!
        for idx in range(len(speech.words)):
            if keyword == speech.words[idx]:
                num_instances += 1
        token_ids[speech.doc_id] = [idx for idx in range(len(speech.words)) if keyword == speech.words[idx]]
    return token_ids, num_instances


"""
Extract speechact spans for a list of token ids
and return the spans as a list.
"""
def extract_speechact_spans(doc_id, tok_id, speech):
    span_dict = {}
    # extract the annot_dict for speechacts
    annot_dict = extract_speechacts([speech]) 
    for idx in annot_dict[doc_id]:
        if annot_dict[doc_id][idx] == []:
            continue
        for item in annot_dict[doc_id][idx]: 
            if tok_id >= item['start'] and tok_id <= item['end']:
                span_dict[idx] = item
    return span_dict


"""
Extract moral frame spans for a list of token ids
and return the spans as a list.
"""
def extract_moral_frame_spans(doc_id, tok_id, speech):
    span_dict = {}
    # extract the annot_dict for moral frames
    annot_dict = extract_moral_frames([speech]) 
    for idx in annot_dict[doc_id]:
        if annot_dict[doc_id][idx] == []:
            continue
        for item in annot_dict[doc_id][idx]:   
            if tok_id >= item['start'] and tok_id <= item['end']+1:                 
                span_dict[idx] = item
    return span_dict




"""

"""
def get_spans(doc_id, tok_ids, speech, layers):
    span_dict = {doc_id:{'text':speech.words, 'annot': {idx:{} for idx in tok_ids}}}

    for layer in layers:
        for tok_id in tok_ids:
            if layer == 'SPEECHACT':
                span_dict[doc_id]['annot'][tok_id][layer] = extract_speechact_spans(doc_id, tok_id, speech)
            elif layer == 'MORAL':
                span_dict[doc_id]['annot'][tok_id][layer] = extract_moral_frame_spans(doc_id, tok_id, speech)
  
    return span_dict



"""
Takes 
a) a dictionary with doc_ids as keys and a list of token ids for each doc_id,
b) a list of Gepadeu objects and 
c) a list of annonation layers.
Extracts the annotation specified in layers for each token id
and returns them as a dictionary.
"""
def get_annotations_by_id(word_ids, speeches, layers):
    annots = {}
    for doc_id, tok_ids in word_ids.items():
        # get the speech for this doc_id
        speech = get_speech_by_docid(speeches, doc_id)
        # extract annotations and spans for the token ids for each layer
        span_dict = get_spans(doc_id, tok_ids, speech, layers)
        annots[doc_id] = span_dict[doc_id]
    return annots
