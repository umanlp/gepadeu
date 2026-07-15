from typing import List
from typing import Any
from dataclasses import dataclass
import spacy
from spacy.tokens.span_group import SpanGroup
from spacy.tokens import Span
from spacy import displacy 
import utils
import csv
import glob
import json
import sys

"""
Gepadeu object: German Parliamentary Debates with rich annotations:

Metadata:
    doc_id      document name
    speech_id   id of speech
    party       speaker affiliation
    date        speech date
    year        speech year
    speaker     speaker name
    term        legislative term
    session     session of the legislative term (e.g., session 18 of the 19th legislative term)

Content:
    words       speech tokens

Annotation layers:
    mope        - Mentions of the People and the Elite (group mentions)
    speechact   - Speech act annotations
    sitent      - Situation entities
    spkatt_annotations - Speaker attribution (events of speech, thought and writing)
    moral       - Moral frame types
    mf          - Moral Foundations
    narrative   - Narrative roles


Dependencies:
- for use in jupyter notebooks, you might have to downgrade ipython to:
    pip install ipython==7.23.1
"""

class Gepadeu:

    def __init__(self, speech_dict):  
        self.doc_id = speech_dict['document_id']
        self.speech_id = speech_dict['speech_id']
        
        # Set source (either speeches taken from GermaParl or Open Bundestag)
        if self.speech_id.startswith('ID'):
            self.source = 'OpenBT'
        else: self.source = 'GermaParl'

        ### Metadata
        self.party = speech_dict['party']
        self.date = speech_dict['date']
        self.year = int(self.date[6:])
        self.speaker = speech_dict['speaker']
        self.term = speech_dict['term']
        self.session = speech_dict['session']
        self.gov_opp = utils.is_gov_opp(self.party, self.term)
        
        ### Speech content
        self.words = speech_dict['words']

        ### Annotation layers
        #   NER layer
        self.ner = speech_dict['ner']
        #   Mentions of the People and the Elite (group mentions)
        self.mope = speech_dict['mope']
        #   Speech act layer
        if 'speechact' in speech_dict:
            self.speechact = speech_dict['speechact']
        #   Situation Entities (SE) layers
        if 'sitent_A' in speech_dict:
            self.sitent = []
            for i in range(len(speech_dict['sitent_A'])):
                if speech_dict['sitent_A'][i] == speech_dict['sitent_B'][i]:
                    self.sitent.append(speech_dict['sitent_A'][i])
                else:
                    self.sitent.append(speech_dict['sitent_A'][i]+','+speech_dict['sitent_B'][i])
        if 'abs_ent_A' in speech_dict:
            self.abs_ent = []
            for i in range(len(speech_dict['abs_ent_A'])):
                if speech_dict['abs_ent_A'][i] == speech_dict['abs_ent_B'][i]:
                    self.abs_ent.append(speech_dict['abs_ent_A'][i])
                else:
                    self.abs_ent.append(speech_dict['abs_ent_A'][i]+','+speech_dict['abs_ent_B'][i])
        else: 
            self.sitent, self.abs_ent = [], []

        #   Speaker attribution layer
        self.spkatt = self.spkatt_BIO_tags_to_dict(speech_dict['spkatt'])
        #   Moral frame layer
        self.moral = speech_dict['moral']


    def add_metainfo(json_dict):
        doc_id = json_dict["document_id"] 
        json_dict['speech_id'] = Gepadeu.get_speech_id(doc_id)
        json_dict['party'] = Gepadeu.get_party(doc_id)
        json_dict['date']  = Gepadeu.get_date(doc_id)
        json_dict['speaker']  = Gepadeu.get_speaker(doc_id)
        term, session = Gepadeu.get_term_session(doc_id)
        json_dict['term']  = term
        json_dict['session']  = session
        return json_dict


    """
    Convert BIO tags into frames (speech triggers) and roles 
    (Addressee, Source, Message...)
    """
    def spkatt_BIO_tags_to_dict(self, dict):
        triggers = ['V', 'PTC']
        spkatt_roles = utils.get_spkatt_role_labels() + triggers
        spk_dict = {role:[] for role in spkatt_roles}

        for trigger_id, roles in dict.items():
            for i in roles.keys():
                if roles[i].startswith('B-'):
                    start = int(i) 
                    role = roles[i].replace('B-', '').replace('I-', '')
                    for j in roles.keys():
                        if j <= i: continue
                        if not roles[j].startswith('I-'):
                            tmp = {
                                'start': start,
                                'end': int(j)-1,
                                'words': self.words[start:int(j)] 
                            }
                            #if not role in triggers:
                            tmp['trigger'] = int(trigger_id)
                            spk_dict[role].append(tmp)
                            break
        return spk_dict




    def get_party(docid):
        # TODO: returns party names for gold standard only 
        # (needs to be adapted to party names in silver standard: parties from 1949-...)
        parties = ['AfD', 'CDU_CSU', 'FDP', 'GRUENE', 'LINKE', 'SPD', 'fraktionslos']
        for party in parties:
            if party in docid:
                return party
            # just in case...
            elif 'Fraktionslos' in docid:
                return 'fraktionslos'
        return "unknown"

    def get_speech_id(docid): 
        return docid.split('_')[-2]

    def get_date(docid): 
        return docid.split('_')[-1]

    def get_speaker(docid): 
        return docid.split('_')[-3]


    def get_term_session(docid): 
        term_session = docid.split('_')[0]
        term = term_session[0:2]
        session = term_session[2:]
        if term[0] == '0':
            term = term[1]
        if session[0] == '0':
            session = session[1:]
        return int(term), int(session)
    

    # Add annotation layers if available 
    # (not all annotation layers exist for all documents)
    def add_missing_layers(json_dict):
        if 'mope' not in json_dict:
            json_dict['mope'] = []
        if 'ner' not in json_dict:
            json_dict['ner'] = []
        if 'speechact' not in json_dict:
            json_dict['speechact'] = []
        if 'sitent' not in json_dict:
            json_dict['sitent'] = []
        if 'moral' not in json_dict:
            json_dict['moral'] = {}
        if 'mf' not in json_dict:
            json_dict['mf'] = {}
        return json_dict


    def from_json(json_string, jfile):
        json_dict = json.loads(json_string)
        json_dict['document_id'] = jfile.split('/')[-1].replace('.json', '')
        json_dict = Gepadeu.add_metainfo(Gepadeu.add_missing_layers(json_dict))
        return Gepadeu(json_dict)


    """
    Takes a dictionary with doc ids as keys and an annotation layer specification and exports the annotations to file.
    """
    def to_csv(annot_dict, content, meta, layer):
        outfile = 'GePaDeU_' + layer + '.csv'
        header = ['doc_id', 'speech_id', 'party', 'date', 'year', 'speaker', 'term', 'session', 'gov_opp', 'source', 'label', 'text']

        with open(outfile, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            for doc_id in annot_dict:
                
                if layer == 'speechact':
                    for idx, annot in annot_dict[doc_id].items():
                        if annot == {}:
                            continue
                        row = [doc_id, meta[doc_id]['speech_id'], meta[doc_id]['party'], meta[doc_id]['date'], meta[doc_id]['year'], meta[doc_id]['speaker'], meta[doc_id]['term'], meta[doc_id]['session'], meta[doc_id]['gov_opp'], meta[doc_id]['source'], idx, " ".join(annot['words'])]
                        writer.writerow(row)

                elif layer == 'spkatt':
                    for idx, annot in annot_dict[doc_id].items():
                        if annot == []:
                            continue
                        for item in annot:
                            row = [doc_id, meta[doc_id]['speech_id'], meta[doc_id]['party'], meta[doc_id]['date'], meta[doc_id]['year'], meta[doc_id]['speaker'], meta[doc_id]['term'], meta[doc_id]['session'], meta[doc_id]['gov_opp'], meta[doc_id]['source'], idx, " ".join(item['words'])]
                            writer.writerow(row) 
   
                elif layer == 'moral':
                    for idx, annot in annot_dict[doc_id].items():
                        if annot == []:
                            continue
                        for item in annot:
                            row = [doc_id, meta[doc_id]['speech_id'], meta[doc_id]['party'], meta[doc_id]['date'], meta[doc_id]['year'], meta[doc_id]['speaker'], meta[doc_id]['term'], meta[doc_id]['session'], meta[doc_id]['gov_opp'], meta[doc_id]['source'], idx, " ".join(item['words'])]
                            writer.writerow(row)  




    """
    Search for keyword and visualise all annotations 
    that overlap with this keyword. 
    Use spacy spans and displacy for visualisation.
    """
    def display_keyword_with_annots(annotations, meta_dict, layers, setting):
        nlp = spacy.blank("de")
        html = ""
        annot_dict = {}

        for doc_id in annotations: 
            annot_set, tok_ids = [], [] 
            tmp = {}  
            annot_dict[doc_id] = {}
            for layer in layers:
                # skip when no annotations are available
                if annotations[doc_id]['annot'] == {}: continue

                for tok_id in annotations[doc_id]['annot']:
                    if layer in annotations[doc_id]['annot'][tok_id] and annotations[doc_id]['annot'][tok_id][layer] != {}: 
                        if tok_id not in tmp: tmp[tok_id] = {}
                        tmp[tok_id][layer] = annotations[doc_id]['annot'][tok_id][layer]

            if tmp != {}:
                annot_set.append(tmp)  

            options = {"spans_key": "sc", "color": "white", "colors": utils.get_colors()}

            # Make the label text white
            css = """
                <style>
                /* label text */
                .entity .label, .spacy-span .label, .spans .label {
                    color: #fff !important;
                }
                </style>
                """ 

            for list_item in annot_set:    
              for tok_id, item in list_item.items():  
                # we need speechact annotations to get the spans
                if not 'speechact' in item: continue 

                annot_dict[doc_id]['speechact'] = {l:0 for l in item['speechact']}

                for label, annot in item['speechact'].items():
                    doc = nlp(" ".join(annot['words']))
                    doc.spans['sc'] = []
                    span_start = item['speechact'][label]['start'] # CHECK
                    doc.spans['sc'].append(Span(doc, 0, len(annot['words']), label))
                    annot_dict[doc_id]['speechact'][label] += 1

                    for layer in layers:
                        if layer != 'speechact' and layer in item:
                            annot_dict[doc_id][layer] = {l:0 for l in item[layer]}
                        else: continue

                        for label, annot in item[layer].items():
                            start = item[layer][label]['start'] - span_start 
                            end = start + (item[layer][label]['end'] - item[layer][label]['start'])
                            doc.spans['sc'].append(Span(doc, start, end, label))
                            annot_dict[doc_id][layer][label] += 1         

                if setting == 'display':
                    try:
                        doc
                    except:
                        pass
                    else: 
                        displacy.render(doc, style="span", options=options)
                        del doc
                elif setting == 'save':
                    try:
                        doc
                    except:
                        pass
                    else:
                        html += displacy.render(doc, style="span", options=options)
                        html += meta_dict[doc_id]['speaker'] + " (" + meta_dict[doc_id]['party'] + "), " + meta_dict[doc_id]['date'] + "<br/><br/>" 
                        del doc

        if setting == 'save':
            with open("data_vis.html", "w") as f:
                f.write(html)

        return annot_dict



    """
    Takes two dictionaries, one with speechact annotations, the other with annotations of Moral Foundations, and displays them.
    Uses spacy spans and displacy for visualisation.
    """
    def display_speechact_mf_annots(speechact_dict, moral_dict, meta_dict, speechact_tag, setting):
        nlp = spacy.blank("de")
        options = {"spans_key": "sc", "color": "white", "colors": utils.get_colors()}
        html = ""
        annot_dict = {party:{mf:0 for mf in utils.get_mf_labels()} for party in utils.get_parties()}

        for doc_id in speechact_dict:
            # get all speechact annotations for the specified label 
            speechacts = [item for item in speechact_dict[doc_id][speechact_tag]]
            if len(speechacts) == 0:
                continue
            morals = moral_dict[doc_id] 

            for item in speechacts: 
                # create a document for each speechact item
                doc = nlp(" ".join(item['words']))
                doc.spans['sc'] = []
                # add the speechact span                 
                span_start = item['start']
                span_end = item['end']
                doc.spans['sc'].append(Span(doc, 0, len(item['words']), speechact_tag))

                # now check for overlapping moral annotations
                for label, annot_list in morals.items():
                    for annot in annot_list:
                        # check if spans for the 2 layers overlap
                        if utils.span_overlap(span_start, span_end, annot['start'], annot['end']): 
                            if annot['start'] < span_start: start = 0
                            else:
                                start = annot['start'] - span_start
                            end = start + (annot['end'] - annot['start'])
                            if end > len(item['words']): end = len(item['words']) 
                            doc.spans['sc'].append(Span(doc, start, end, label))
                            annot_dict[meta_dict[doc_id]['party']][label] += 1
                    
                if setting == 'display':
                    try:
                        doc
                    except:
                        pass 
                    else:
                        displacy.render(doc, style="span", options=options)
                        #print(meta_dict[doc_id]['speaker'] + " (" + meta_dict[doc_id]['party'] + "), " + meta_dict[doc_id]['date'] + "\n")
                    del doc
                elif setting == 'save':
                    try:
                        doc
                    except:
                        pass 
                    else:
                        html += displacy.render(doc, style="span", options=options)
                        html += meta_dict[doc_id]['speaker'] + " (" + meta_dict[doc_id]['party'] + "), " + meta_dict[doc_id]['date'] + "<br/><br/>" 
                    del doc

        if setting == 'save':
            with open("data_vis.html", "w") as f:
                f.write(html)

        return annot_dict


            



    """
    Display speech act annotations
    """
    def display_speechact_annotations(annot_tuple, tag, meta_dict, setting):
        nlp = spacy.blank("de")
        html = ""
        docs = []
        annot_dict = {party:[] for party in utils.get_parties()}
        for doc_id, item in annot_tuple: 
            options = {"spans_key": "sc", "color": "white", "colors": utils.get_colors()}
            doc = nlp(" ".join(item['words']))    
            doc.spans['sc'] = [(Span(doc, 0, len(item['words']), tag))]
            annot_dict[meta_dict[doc_id]['party']].append(item)
            if setting == 'display':
                try:
                    doc
                except:
                    pass
                else:
                    displacy.render(doc, style="span", options=options)
                    docs.append(doc)
                del doc
            elif setting == 'save':
                try:
                    doc
                except:
                    pass
                else:
                    html += displacy.render(doc, style="span", options=options)
                    html += meta_dict[doc_id]['speaker'] + " (" + meta_dict[doc_id]['party'] + "), " + meta_dict[doc_id]['date'] + "<br/><br/>" 
                    docs.append(doc)
                del doc

        if setting == 'save':
            with open("data_vis.html", "w") as f:
                f.write(html)

        return annot_dict

 
