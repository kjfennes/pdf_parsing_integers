Running this file assumes the following have already been run:

pip install pymupdf
pip install spacy
python -m spacy download en_core_web_sm

It also assumes that the file FY25 Air Force Working Capital Fund.pdf is in the current working directory, or its location is updated in the code.

This can be run with 

python find_largest_number.py

and its results should print and look something like 

{'value': 52791000000, 'original_text': '$5,279.1', 'page_number': 54}
