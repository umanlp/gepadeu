import gepadeu
from pprint import pprint
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


# List all parties that had a function in all legislative terms of the BRD
# and specify the function (either government or opposition).
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
            # FIXME: What happened in this term?
            # Koalitionsbruch?
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


# TODO: returns party names for gold standard only 
# (needs to be adapted for party names in the silver standard: 
# parties that took part in the Bundestag from 1949 to today)
def get_parties():
    return ['AfD', 'CDU_CSU', 'FDP', 'GRUENE', 'LINKE', 'SPD', 'fraktionslos']

def get_speechact_labels():
    return ['Accusation', 'Bad-outcome', 'Demand', 'Evaluation', 'Expressive', 'I-S-Humour', 'Macro', 'Question-All', 'Promise', 'Rejection', 'Report', 'Request', 'Self-representation', 'Support']

def get_moral_frame_labels():
    return ['MoralValue', 'ImmoralValue', 'MoralActOrGoal', 'ImmoralActOrGoal', 'PoliticalActOrGoal']

def get_mf_labels():
    return ['Authority', 'Care', 'Equality', 'Liberty', 'Loyalty', 'Proportionality', 'Purity', 'General-Moral']

def get_narrative_role_labels():
    return ['Beneficiary', 'Hero', 'Victim', 'Villain']

def get_spkatt_role_labels():
    return ['Addr', 'Source', 'Message', 'Topic', 'Medium', 'Evidence']

def get_spkatt_trigger_labels():
    return ['V', 'PTC']

def get_mope_labels():
    return ['eoFinanz', 'eoMedia', 'eoMil', 'eoMov', 'eoNgo', 'eoPol', 'eoRel', 'eoSci', 'eoWirt', 'epFinanz', 'epKult', 'epMedia', 'epMil', 'epMov', 'epNgo', 'epOwn', 'epPol', 'epRel', 'epSci', 'epWirt', 'GPE', 'pAge', 'pEth', 'pFunk', 'pGen', 'pNat', 'pSoz']

# Convert mappings to more readable label names.
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
    return ['STATE', 'EVENT', 'REPORT', 'GENERIC', 'GENERALIZING', 'EVENT-PERFECT-STATE', 'IMPERATIVE', 'QUESTION']
    

def get_abs_ent_labels():
    return ['FACT', 'PROPOSITION']
    

# Check if two lists (indicated by their start and end indices) overlap
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
Attention: This is only an approximation when applied to a larger corpus as there might be several politicians with the same last name affiliated with the same party.
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


def get_number_of_spkatt_triggers(speeches):
    triggers = 0
    memory = {}
    for speech in speeches:
        memory[speech.doc_id] = {}
        spkatt_dict = speech.spkatt
        # count number of spkatt 
        for label in spkatt_dict:
            for item in spkatt_dict[label]:
                if item['trigger'] not in memory[speech.doc_id]:
                    triggers += 1
                    memory[speech.doc_id][item['trigger']] = 0
                memory[speech.doc_id][item['trigger']] += 1
    return triggers


def get_number_of_spkatt_roles(speeches):
    spkatt = 0 
    for speech in speeches:
        spkatt_dict = speech.spkatt
        # count number of spkatt 
        for label in spkatt_dict:
            spkatt += len(spkatt_dict[label])
    return spkatt


def get_number_of_mope_mentions(speeches):
    mope = 0
    mope_dict = extract_mope(speeches) 
    # count number of mope 
    for doc_id in mope_dict: 
        for label in mope_dict[doc_id]:
            mope += len(mope_dict[doc_id][label])
    return mope


def get_number_of_named_entities(speeches):
    ne = 0
    ne_dict = extract_ner(speeches) 
    # count number of named entities
    for doc_id in ne_dict: 
        for label in ne_dict[doc_id]:
            ne += len(ne_dict[doc_id][label])
    return ne


def get_number_of_sitents(speeches):
    sitent = 0
    sitent_dict = extract_sitent(speeches) 
    # count number of sitent
    for doc_id in sitent_dict: 
        for label in sitent_dict[doc_id]:
            sitent += len(sitent_dict[doc_id][label])
    return sitent


def get_number_of_abs_ents(speeches):
    abs_ent = 0
    abs_ent_dict = extract_abs_ent(speeches) 
    # count number of sitent
    for doc_id in abs_ent_dict: 
        for label in abs_ent_dict[doc_id]:
            abs_ent += len(abs_ent_dict[doc_id][label])
    return abs_ent


def get_number_of_moral_frames(speeches):
    frames = 0
    frame_dict = extract_moral_frames(speeches) 
    # count number of moral frames 
    for doc_id in frame_dict: 
        for label in frame_dict[doc_id]:
            frames += len(frame_dict[doc_id][label])
    return frames


def get_number_of_narrative_roles(speeches):
    roles = 0
    frame_dict = extract_narrative_roles(speeches) 
    # count number of moral frames 
    for doc_id in frame_dict: 
        for role in frame_dict[doc_id]:
            roles += len(frame_dict[doc_id][role])
    return roles


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
Takes a dictionary with annotations for a given keyword and prints the number of 
annotations for each party and label for the specified layer.
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
Takes a list of speeches (Gepadeu objects) and extracts some corpus statistics.

Returns a dictionary with doc_ids as keys and the metadata for each key.
"""
def extract_stats(speeches):
    parties = ['AfD', 'CDU_CSU', 'FDP', 'GRUENE', 'LINKE', 'SPD', 'fraktionslos']
    meta_dict = extract_metadata(speeches)
    
    stats_dict = {
        # corpus sizes
        'speeches': len(speeches),
        'speakers': get_number_of_speakers(speeches),
        'parties': get_number_of_parties(speeches),

        # numbers per party/year/term
        'speeches_per_party': get_speeches_per_party(speeches, parties),
        'speeches_per_year': get_speeches_per_year(speeches),
        'speeches_per_term': get_speeches_per_term(speeches),

        # no. of instances per annotation layer
        'mope': get_number_of_mope_mentions(speeches), 
        'moral': get_number_of_moral_frames(speeches), 
        'narrative': get_number_of_narrative_roles(speeches), 
        'ner': get_number_of_named_entities(speeches),
        'sitent': get_number_of_sitents(speeches),
        'abs_ent': get_number_of_abs_ents(speeches),
        'speechact': get_number_of_speechacts(speeches),
        'spkatt_trigger': get_number_of_spkatt_triggers(speeches),
        'spkatt_roles': get_number_of_spkatt_roles(speeches),

        # no. of instances per party, for different label categories
        'mope_mentions_per_party': get_mope_per_party(speeches, parties, meta_dict),  
        'moral_frames_per_party': get_moral_frames_per_party(speeches, parties, meta_dict),
        'mf_per_party': get_mf_per_party(speeches, parties, meta_dict),
        'ner_per_party': get_ner_per_party(speeches, parties, meta_dict),  
        'speechacts_per_party': get_speechacts_per_party(speeches, parties, meta_dict),  
        'spkatt_roles_per_party': get_spkatt_roles_per_party(speeches, parties, meta_dict),
        'sitent_per_party': get_sitent_per_party(speeches, parties, meta_dict),
        'abs_ent_per_party': get_abs_ent_per_party(speeches, parties, meta_dict),
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

        for i in range(len(speech.speechact)): 
            if speech.speechact[i].startswith('B-'):
                start = i
                elms = speech.speechact[i].replace('B-', '').split(',')
                for label in elms:
                    for j in range(i+1, len(speech.speechact)):
                        if not speech.speechact[j].startswith('I-'):
                            tmp = {
                                'start': start,
                                'end': j-1,
                                'words': speech.words[start:j] 
                            }
                            speechact_dict[speech.doc_id][label].append(tmp)
                            break
    return speechact_dict



def extract_sitent(speeches):
    sitents = get_sitent_labels()
    sitent_dict = {}
    for speech in speeches:
        sitent_dict[speech.doc_id] = {sitent:[] for sitent in sitents} 

        for i in range(len(speech.sitent)): 
            labels = speech.sitent[i].split(',')
            for label in labels:
                if label != "_":
                    tmp = {
                        'id': i, 
                        'words': speech.words[i] 
                    }
                    sitent_dict[speech.doc_id][label].append(tmp)

    return sitent_dict


def extract_abs_ent(speeches):
    abs_ents = get_abs_ent_labels()
    abs_ent_dict = {}
    for speech in speeches:
        abs_ent_dict[speech.doc_id] = {abs_ent:[] for abs_ent in abs_ents} 

        for i in range(len(speech.abs_ent)): 
            labels = speech.abs_ent[i].split(',')
            for label in labels:
                if label != "_":
                    tmp = {
                        'id': i, 
                        'words': speech.words[i] 
                    }
                    abs_ent_dict[speech.doc_id][label].append(tmp)

    return abs_ent_dict



def get_sitent_per_party(speeches, parties, meta_dict):
    sitent_dict = extract_sitent(speeches)
    # get list of situation entities
    sitent = list(set([l for docid in sitent_dict for l in sitent_dict[docid]]))
    stats_dict = {party:{label:0 for label in sitent} for party in parties}
    # count number of sitents per party
    for doc_id in sitent_dict: 
        for label in sitent_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][label] += len(sitent_dict[doc_id][label])

    return stats_dict


def get_abs_ent_per_party(speeches, parties, meta_dict):
    abs_ent_dict = extract_abs_ent(speeches)
    # get list of situation entities
    abs_ent = list(set([l for docid in abs_ent_dict for l in abs_ent_dict[docid]]))
    stats_dict = {party:{label:0 for label in abs_ent} for party in parties}
    # count number of abstract objects per party
    for doc_id in abs_ent_dict: 
        for label in abs_ent_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][label] += len(abs_ent_dict[doc_id][label])

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
    # get list of mope categories
    mope = list(set([l for docid in mope_dict for l in mope_dict[docid]]))
    stats_dict = {party:{label:0 for label in mope} for party in parties}
    # count number of group mentions per party
    for doc_id in mope_dict: 
        for label in mope_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][label] += len(mope_dict[doc_id][label])

    return stats_dict



def get_ner_per_party(speeches, parties, meta_dict):
    ner_dict = extract_ner(speeches)
    # get list of NER tags
    ner = list(set([l for docid in ner_dict for l in ner_dict[docid]]))
    stats_dict = {party:{label:0 for label in ner} for party in parties}
    # count number of NER tags per party
    for doc_id in ner_dict: 
        for label in ner_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][label] += len(ner_dict[doc_id][label])

    return stats_dict



def get_moral_frames_per_party(speeches, parties, meta_dict):
    moral_dict = extract_moral_frames(speeches)
    # get list of moral frame types
    frames = list(set([mtype for docid in moral_dict for mtype in moral_dict[docid]])) 
    stats_dict = {party:{ft:0 for ft in frames} for party in parties}
    # count number of moral frames per party 
    for doc_id in moral_dict: 
        for ft in moral_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][ft] += len(moral_dict[doc_id][ft])

    return stats_dict


def get_mf_per_party(speeches, parties, meta_dict):
    moral_dict = extract_mf(speeches)
    # get list of moral foundations
    mfs = list(set([mf for docid in moral_dict for mf in moral_dict[docid]])) 
    stats_dict = {party:{mf:0 for mf in mfs} for party in parties}
    # count number of moral foundations per party 
    for doc_id in moral_dict: 
        for mf in moral_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][mf] += len(moral_dict[doc_id][mf])

    return stats_dict



def get_spkatt_roles_per_party(speeches, parties, meta_dict):
    spkatt_dict = extract_spkatt(speeches)
    # get list of spkatt roles
    roles = list(set([role for docid in spkatt_dict for role in spkatt_dict[docid]])) 
    stats_dict = {party:{role:0 for role in roles} for party in parties}
    # count number of spkatt annotations for each role
    for doc_id in spkatt_dict: 
        for role in spkatt_dict[doc_id]:
            stats_dict[meta_dict[doc_id]['party']][role] += len(spkatt_dict[doc_id][role])

    return stats_dict




"""
Takes a list of speeches (Gepadeu objects) and extracts all named entities (NE).
Returns a dictionary with doc_ids as keys, with NE types for each doc.
"""
def extract_ner(speeches):
    ner_tags = ['AGE', 'ART', 'CARDINAL', 'DATE', 'DUR', 'EVT', 'FAC', 'FRAC', 'FREQ', 'GPE', 'LAN', 'LAW', 'LOC', 'MED', 'MISC', 'MON', 'NRP', 'ORDINAL', 'ORG', 'PER', 'PERC', 'PRODUCT', 'PROJ', 'QUANT', 'RATE', 'SCORE', 'SORD', 'TIME', 'TITLE', 'URL']
    ner_dict = {}
    
    for speech in speeches:
        ner_dict[speech.doc_id] = {}
        for i in range(len(speech.ner)):
            this_tag = speech.ner[i].replace('B-', '').replace('I-', '')
            if this_tag in ner_tags:
                this_annot = {'start':0, 'end':0}
                if i > 0:
                    prev_tag = speech.ner[i-1].replace('B-', '').replace('I-', '')
                    if prev_tag != this_tag:
                        this_annot['start'] = i
                        for j in range(i+1, len(speech.ner)): 
                            if speech.ner[j-i].endswith(this_tag):
                                this_annot['end'] = j-1
                                this_annot['words'] = speech.words[i:j-1]
                                ner_dict[speech.doc_id][this_tag] = this_annot

    return ner_dict


"""                
Takes a list of speeches (Gepadeu objects) and extracts all moral frames.
Returns a dictionary with doc_ids as keys, sorted by the frame type of the moral frame.
"""
def extract_moral_frames(speeches):
    frame_types = get_moral_frame_labels()
    moral_dict = {}
    for speech in speeches:
        moral_dict[speech.doc_id] = {mtype:[] for mtype in frame_types} 
        for mdic in speech.moral:
            frame_type = mdic['frame_type']
            frame_span = mdic['frame_ids']
            words = speech.words[frame_span[0]:frame_span[-1]+1]
            moral_dict[speech.doc_id][frame_type].append({'start': frame_span[0], 'end': frame_span[-1]+1, 'words': words})
    return moral_dict



"""
Takes a list of speeches (Gepadeu objects) and extracts all moral frames.
Returns a dictionary with doc_ids as keys, sorted by the mf of the moral frame.
"""
def extract_mf(speeches):
    mfs = get_mf_labels()
    moral_dict = {}
    for speech in speeches:
        moral_dict[speech.doc_id] = {mf:[] for mf in mfs} 
        for mdic in speech.moral:
            mf_vote = []
            frame_type = mdic['frame_type']
            if frame_type != 'PoliticalActOrGoal':
                mf_vote = mdic['MF_majority']
            frame_span = mdic['frame_ids']
            words = speech.words[frame_span[0]:frame_span[-1]+1]
            for mf in mf_vote:
                if mf not in mfs: # Skip annotations that have been identified as PoliticalActOrGoal during manual validation.
                    continue 
                moral_dict[speech.doc_id][mf].append({'start': frame_span[0], 'end': frame_span[-1]+1, 'words': words})
    return moral_dict


"""
Takes a list of speeches (Gepadeu objects) and extracts all narrative roles for the moral frames.
Returns a dictionary with doc_ids as keys, sorted by narrative roles.
"""
def extract_narrative_roles(speeches):
    roles = get_narrative_role_labels()
    role_dict = {}
    for speech in speeches:
        role_dict[speech.doc_id] = {role:[] for role in roles} 
        for mdic in speech.moral:
            for role in roles:
                if role in mdic:
                    role_span = mdic[role]
                    words = speech.words[role_span[0]-1:role_span[-1]]
                    role_dict[speech.doc_id][role].append({'start': role_span[0]-1, 'end': role_span[-1], 'words': words})

    return role_dict


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
            if speech.mope[i] == 'O' or speech.mope[i] == '_':
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

Spk Att Dict {
   "19124_Tagesordnungspunkt_3_CDU_CSU_Winkelmeier-Becker_ID1912400900_07.11.2019": {
      "Addressee": [],
      "Source": [
         {
            "start": 5,
            "end": 5,
            "words": [
               "wir"
            ]
         },...,
         {
            "start": 8,
            "end": 10,
            "words": [
               "des",
               "Kollegen",
               "Seitz"
            ]
         },

"""
def extract_spkatt(speeches):
    spkatt_dict = {}
    for speech in speeches:
        spkatt_dict[speech.doc_id] = speech.spkatt

    return spkatt_dict



"""
Takes a list of speeches (Gepadeu objects) and a token string (keyword) and returns all token ids for this token as a list.
"""
def search_for(speeches, keyword):
    token_ids = {}; num_instances = 0
    for speech in speeches:
        # We only consider token matches, no subtokens!
        for idx in range(len(speech.words)):
            if keyword == speech.words[idx]:
                num_instances += 1
        token_ids[speech.doc_id] = [idx for idx in range(len(speech.words)) if keyword == speech.words[idx]]
    return token_ids, num_instances


"""
Extract speechact spans for a list of token ids and return the spans as a list.
"""
def extract_speechact_spans(doc_id, tok_id, speech):
    span_dict = {}
    # Extract the annot_dict for speechacts
    annot_dict = extract_speechacts([speech]) 
    for label in annot_dict[doc_id]: 
        for item in annot_dict[doc_id][label]: 
            if tok_id >= item['start'] and tok_id <= item['end']:
                span_dict[label] = item
    return span_dict


"""
Extract moral frame spans for a list of token ids
and return the spans as a list.
"""
def extract_moral_frame_spans(doc_id, tok_id, speech):
    span_dict = {}
    # Extract the annot_dict for moral frames
    annot_dict = extract_moral_frames([speech]) 
    for mframe in annot_dict[doc_id]:
        if annot_dict[doc_id][mframe] == []:
            continue
        for item in annot_dict[doc_id][mframe]:   
            if tok_id >= item['start'] and tok_id <= item['end']+1:                 
                span_dict[mframe] = item
    return span_dict


"""
Extract Moral Foundation frame spans for a list of token ids
and return the spans as a list.
"""
def extract_mf_frame_spans(doc_id, tok_id, speech):
    span_dict = {}
    # Extract the annot_dict for moral frames
    annot_dict = extract_mf([speech]) 
    for mf in annot_dict[doc_id]:
        if annot_dict[doc_id][mf] == []:
            continue
        for item in annot_dict[doc_id][mf]:   
            if tok_id >= item['start'] and tok_id <= item['end']:                 
                span_dict[mf] = item
    return span_dict


"""
Extract spans for different annotation layers.
ToDo: expand for other layers (spkatt, mope, NER, sitent)
"""
def get_spans(doc_id, tok_ids, speech, layers):
    span_dict = {doc_id:{'text':speech.words, 'annot': {idx:{} for idx in tok_ids}}}

    for layer in layers:
        for tok_id in tok_ids:
            if layer == 'speechact':
                span_dict[doc_id]['annot'][tok_id][layer] = extract_speechact_spans(doc_id, tok_id, speech)
            elif layer == 'moral':
                span_dict[doc_id]['annot'][tok_id][layer] = extract_moral_frame_spans(doc_id, tok_id, speech)
            elif layer == 'mf':
                span_dict[doc_id]['annot'][tok_id][layer] = extract_mf_frame_spans(doc_id, tok_id, speech)

    return span_dict



"""
Takes 
a) a dictionary with doc_ids as keys and a list of token ids for each doc_id,
b) a list of Gepadeu objects and 
c) a list of annonation layers.
Extracts the annotation specified in layers for each token id
and returns them as a dictionary.
"""
def get_annotations_by_id(keyword_ids, speeches, layers):
    annots = {}
    for doc_id, tok_ids in keyword_ids.items():
        if tok_ids == []: continue
        # Get the speech for this doc_id
        speech = get_speech_by_docid(speeches, doc_id)
        # Extract annotations and spans for the token ids for each layer
        span_dict = get_spans(doc_id, tok_ids, speech, layers)
        annots[doc_id] = span_dict[doc_id]
    return annots
