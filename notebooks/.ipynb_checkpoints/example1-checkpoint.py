import gepader
import utils
import json
import glob
import sys

indir = '../speeches'
jfiles = glob.glob(indir + '/*.json')
speeches = []

# read in all files and convert to Gepader objects
for jfile in jfiles: 
    with open(jfile, 'r') as inf: 
        speeches.append(gepader.Gepader.from_json(inf.read())) 

# extract content for each speech
content_dict = utils.extract_content(speeches)

# extract metadata for each speech
meta_dict = utils.extract_metadata(speeches)

# Search for specific words and return their token ids as a list
word = 'Freiheit'
word_ids = utils.search_for(speeches, word)
# Get all annotations (if any) for those words
annotations = utils.get_annotations_by_id(word_ids, speeches, ['SPEECHACT', 'MORAL'])

#print(json.dumps(annotations, indent=3))
gepader.Gepader.visualise_annotations(annotations, meta_dict, word)

sys.exit()

stats_dict = utils.extract_stats(speeches)
print("STATS")
print(json.dumps(stats_dict, indent=3))
sys.exit()

moral_dict = utils.extract_moral_frames(speeches)
#print("MDD")
#print(json.dumps(moral_dict, indent=3))
#sys.exit()

# extract all speaker attribution 
spkatt_dict = utils.extract_spkatt(speeches) 


# sort speeches by party
party_dict = utils.sort_speeches_by_party(speeches)

# sort speeches by term
term_dict = utils.sort_speeches_by_term(speeches)

# sort speeches by year
year_dict = utils.sort_speeches_by_year(speeches)

# extract all SPEECH_ACTs
speechact_dict = utils.extract_speechacts(speeches)

# extract all moral frames 
moral_dict = utils.extract_moral_frames(speeches)

# extract all MOPE entities 
#mope_dict = utils.extract_mope(speeches)

# extract all NER entities 
#ner_dict = utils.extract_ner(speeches)

# extract all SITENT (situation entity types)
#sitent_dict = utils.extract_sitent(speeches)

# 

# compare annotations for one layer across parties
#speechact_dict_sorted = utils.sort_annots_by_party(speechact_dict, meta_dict)
#print()
#print(json.dumps(speechact_dict_sorted, indent=3))
#sys.exit()



# compare annotations for one layer over time

# export single annotation layers to csv 
### a) merge annotations with text
### b) export to json file
gepader.Gepader.to_csv(moral_dict, content_dict, meta_dict, 'MORAL')

#utils.speech_by_docid(content_dic, doc_id)

print("\nMORAL")
print(moral_dict)
sys.exit()

print()
print("TERM")
print(term_dict[19][0:3])



sys.exit()


print()
print("YEAR")
print(year_dict[2018][0:3])


print()
print("GRUENE")
print(party_dict["FDP"][0:3])
