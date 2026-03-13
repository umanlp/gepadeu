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
    mope
    mope_units
    speechact
    sitent
    sitent_units
    spkatt_annotations
    spkatt_units
    moral
    moral_units

"""

class Gepadeu:
    def __init__(self, speech_dict):  
        self.doc_id = speech_dict['document_id']
        self.speech_id = speech_dict['speech_id']
        # set source (texts from GermaParl vs Open Bundestag)
        if self.speech_id.startswith('ID'):
            self.source = 'OpenBT'
        else: self.source = 'GermaParl'

        self.party = speech_dict['party']
        self.date = speech_dict['date']
        self.year = int(self.date[6:])
        self.speaker = speech_dict['speaker']
        self.term = speech_dict['term']
        self.session = speech_dict['session']
        self.words = speech_dict['words']
        self.ner = speech_dict['NER']
        self.mope = speech_dict['MOPE']
        self.mope_units = speech_dict['MOPE_units']
        if 'SPEECHACT' in speech_dict:
            self.speechact = speech_dict['SPEECHACT']
        if 'SITENT_annotations' in speech_dict:
            self.sitent = speech_dict['SITENT_annotations']
            self.sitent_units = speech_dict['SITENT_units']
        else: 
            self.sitent, self.sitent_units = {}, {}
        self.spkatt = speech_dict['SPKATT_annotations']
        self.spkatt_units = speech_dict['SPKATT_units']
        self.moral = speech_dict['MORAL']
        self.moral_units = speech_dict['MORAL_units']
        self.gov_opp = utils.is_gov_opp(self.party, self.term)

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



    def get_party(docid):
        # TODO: valid for gold standard only (needs to be adapted to party names in silver standard)
        parties = ['AfD', 'CDU_CSU', 'FDP', 'GRUENE', 'LINKE', 'SPD', 'fraktionslos']
        for party in parties:
            if party in docid:
                return party 
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


    def add_missing_layers(json_dict):
        if 'MOPE' not in json_dict:
            json_dict['MOPE'] = []
        if 'MOPE_units' not in json_dict:
            json_dict['MOPE_units'] = []
        if 'NER' not in json_dict:
            json_dict['NER'] = []
        if 'NER_units' not in json_dict:
            json_dict['NER_units'] = []
        if 'SPEECHACT' not in json_dict:
            json_dict['SPEECHACT'] = {}
        if 'SITENT' not in json_dict:
            json_dict['SITENT'] = {}
        if 'SITENT_units' not in json_dict:
            json_dict['SITENT_units'] = {}
        if 'SPKATT_annotations' not in json_dict:
            json_dict['SPKATT_annotations'] = {}
        if 'SPKATT_units' not in json_dict:
            json_dict['SPKATT_units'] = {}
        if 'MORAL' not in json_dict:
            json_dict['MORAL'] = {}
        if 'MORAL_units' not in json_dict:
            json_dict['MORAL_units'] = {}
        return json_dict




    def from_json(json_string):
        json_dict = json.loads(json_string)
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
                
                if layer == 'SPEECHACT':
                    for idx, annot in annot_dict[doc_id].items():
                        if annot == {}:
                            continue
                        row = [doc_id, meta[doc_id]['speech_id'], meta[doc_id]['party'], meta[doc_id]['date'], meta[doc_id]['year'], meta[doc_id]['speaker'], meta[doc_id]['term'], meta[doc_id]['session'], meta[doc_id]['gov_opp'], meta[doc_id]['source'], idx, " ".join(annot['words'])]
                        writer.writerow(row)

                elif layer == 'SPKATT':
                    for idx, annot in annot_dict[doc_id].items():
                        if annot == []:
                            continue
                        for item in annot:
                            row = [doc_id, meta[doc_id]['speech_id'], meta[doc_id]['party'], meta[doc_id]['date'], meta[doc_id]['year'], meta[doc_id]['speaker'], meta[doc_id]['term'], meta[doc_id]['session'], meta[doc_id]['gov_opp'], meta[doc_id]['source'], idx, " ".join(item['words'])]
                            writer.writerow(row) 
   
                elif layer == 'MORAL':
                    for idx, annot in annot_dict[doc_id].items():
                        if annot == []:
                            continue
                        for item in annot:
                            row = [doc_id, meta[doc_id]['speech_id'], meta[doc_id]['party'], meta[doc_id]['date'], meta[doc_id]['year'], meta[doc_id]['speaker'], meta[doc_id]['term'], meta[doc_id]['session'], meta[doc_id]['gov_opp'], meta[doc_id]['source'], idx, " ".join(item['words'])]
                            writer.writerow(row)  





    def display_instances_per_party(annotations, meta_dict, word, layers):
        for doc_id in annotations: 
            annot_set, tok_ids = [], [] 
            tmp = {}  
            for layer in layers:
                if annotations[doc_id]['annot'] == {}:
                    continue
                for tok_id in annotations[doc_id]['annot']:
                    if annotations[doc_id]['annot'][tok_id][layer] != {}: 
                        if 'annot' not in tmp: tmp['annot'] = {}
                        tmp['annot'][layer] = annotations[doc_id]['annot'][tok_id][layer]
            if tmp != {}:
                    tmp['text'] = annotations[doc_id]['text']
                    annot_set.append(tmp)  

    """
    Search for keyword and visualise speechacts that contain 
    this keyword.
    Add additional annotation layers to the spans.
    Use spacy spans and displacy for visualisation.
    """
    def display_keyword_with_annots(annotations, meta_dict, word, layers, setting):
        nlp = spacy.blank("de")
        html = ""
        annot_dict = {}
        for doc_id in annotations: 
            annot_set, tok_ids = [], [] 
            tmp = {}  
            annot_dict[doc_id] = {}
            for layer in layers:
                if annotations[doc_id]['annot'] == {}:
                    continue
                for tok_id in annotations[doc_id]['annot']:
                    if annotations[doc_id]['annot'][tok_id][layer] != {}: 
                        if tok_id not in tmp: tmp[tok_id] = {}
                        tmp[tok_id][layer] = annotations[doc_id]['annot'][tok_id][layer]
            if tmp != {}:
                tmp['text'] = annotations[doc_id]['text']
                annot_set.append(tmp)  

            #TODO: check for overlap in annot_set (annots for tok_id on different layers should overlap)
            options = {"spans_key": "sc", "color": "white", "colors": utils.get_colors()}

            for list_item in annot_set:    
              for tok_id, item in list_item.items():  
                if 'SPEECHACT' in item:
                  annot_dict[doc_id]['SPEECHACT'] = {l:0 for l in item['SPEECHACT']}
                  for label, annot in item['SPEECHACT'].items():
                    doc = nlp(" ".join(annot['words']))
                    doc.spans['sc'] = []
                    
                    span_start = item['SPEECHACT'][label]['start']
                    doc.spans['sc'].append(Span(doc, 0, len(annot['words']), label))
                    annot_dict[doc_id]['SPEECHACT'][label] += 1
                    
                    if 'MORAL' in layers:
                        if 'MORAL' in item:
                          annot_dict[doc_id]['MORAL'] = {l:0 for l in item['MORAL']}

                          print("MORAL", annot_dict[doc_id])

                          for label, annot in item['MORAL'].items():
                            start = item['MORAL'][label]['start'] - span_start
                            end = start + (item['MORAL'][label]['end'] - item['MORAL'][label]['start'])
                            print("SPAN", start, end, doc)
                            doc.spans['sc'].append(Span(doc, start, end, label))
                            annot_dict[doc_id]['MORAL'][label] += 1         

                if setting == 'display':
                    try:
                        doc
                    except:
                        pass
                    else: 
                        displacy.render(doc, style="span", options=options)
                        print(meta_dict[doc_id]['speaker'] + " (" + meta_dict[doc_id]['party'] + "), " + meta_dict[doc_id]['date'] + "\n")
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
    Takes two dictionaries with span annotations and displays them.
    Uses spacy spans and displacy for visualisation.
    """
    def display_annots(speechact_dict, moral_dict, meta_dict, speechact_tag, setting):
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
                        print(meta_dict[doc_id]['speaker'] + " (" + meta_dict[doc_id]['party'] + "), " + meta_dict[doc_id]['date'] + "\n")
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
            with open("data_example_01.html", "w") as f:
                f.write(html)

        return annot_dict



    """

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
                    print(meta_dict[doc_id]['speaker'] + " (" + meta_dict[doc_id]['party'] + "), " + meta_dict[doc_id]['date'] + "\n")
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
            with open("data_example02.html", "w") as f:
                f.write(html)

        return annot_dict


    """
    """
    def add_annot_layer_and_display(annot_dict, moral_dict, meta_dict, setting):
        nlp = spacy.blank("de")
        html = ""
        docs = []
        html = "" 
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
                    print(meta_dict[doc_id]['speaker'] + " (" + meta_dict[doc_id]['party'] + "), " + meta_dict[doc_id]['date'] + "\n")
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
            with open("data_example03.html", "w") as f:
                f.write(html)

        return docs



    """
    Takes a dictionary with doc ids as keys and an annotation layer specification and exports the annotations to file.
    """
    def annotations_to_csv(annotations, meta_dict, word):
        outfile = 'GePaDeU_' + word + '.csv'
        header = ['doc_id', 'speech_id', 'party', 'date', 'year', 'speaker', 'term', 'session', 'gov_opp', 'source', 'label', 'text']

        with open(outfile, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            #for doc_id in annot_dict:
        return
