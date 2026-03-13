# GePaDeU – A Multi-layer Corpus of German Parliamentary Debates with Rich Semantic and Pragmatic Annotations 

This repository contains the annotation guidelines, data sheet and manual annotations for GePaDeU (German Parliamentary Debates Unified), a multi-layer corpus with unified layers of rich semantic and pragmatic annotations, as supplementary material for our LREC 2026 submission.


------
### Contents of this repository:

```text
gepadeu
├── guidelines
│   ├── Onto_NER_DE.pdf  (from Ruppenhofer et al. (2020))
│   ├── MoPE_Annotation_Guidelines.pdf
│   ├── SitEnt_Annotation_Guidelines.pdf
│   ├── SpkAtt_Annotation_Guidelines.pdf (in German)
│   ├── Speechact_Annotation_Guidelines.pdf
│   └── MoralFrames_Annotation_Guidelines.pdf
├── data
│   └── speeches (to be added soon)
├── notebooks
│   ├── 01_example_basic_statistics.ipynb
│   ├── 02_example_keyword_search.ipynb
│   ├── 03_example_moral_rhetoric.ipynb
│   ├── gepadeu.py
│   └── utils.py
├── README.md
```

------


#### Dependencies

To run the notebooks, create a conda virtual environment and install the following packages:

```
 conda create -n gepadeu python=3.13

 conda activate gepadeu

 pip install notebook
 pip install pandas
 pip install matplotlib
 pip install spacy

 python -m spacy download de_core_news_sm
```


#### Start Jupyter notebook

You can start the notebooks with the following command:

```
 cd notebooks/

 jupyter notebook
```



### References

Ruppenhofer et al. 2020. Fine-grained Named Entity Annotations for German Biographic Interviews. In Proceedings of the Twelfth Language Resources and Evaluation Conference, pages 4605–4614, Marseille, France. European Language Resources Association.





