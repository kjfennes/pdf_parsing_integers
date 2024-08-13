import fitz
from spacy import load
import numerizer
import math
import re

def check_update_max(numerized_dict, page_number, max_num):
    for key, value in numerized_dict.items():
        numlist = re.findall(r'\d+', value)
        for numtext in numlist:
            if int(numtext)>max_num["value"]:
                max_num["value"]=int(numtext)
                max_num["original_text"]=key
                max_num["page_number"]=page_number

'''
some tables have a scale factor in millions, etc
only parsing those separately if we find such a scale.
Otherwise, the numbers from tables would be parsed like any other text.
'''

#add commonly used scales mentioned in tables
table_scale_indentifiers = {
    "in millions": 1000000,
    "$M": 1000000,
    "$ millions": 1000000,
    "in billions": 1000000000,
    "$B": 1000000000,    
    "in thousands": 1000,  
}

def check_for_scale_identifiers(row_list):
    try:
        for key, value in table_scale_indentifiers.items():
            if any(key in item.lower() for item in row_list):
                return value
    except:
        return 1
    return 1

def update_max_with_scaled_table_val(table_data, scale_factor, page_number, max_num):
    for row in table_data:
        for val in row:
            #parenthesis may  indicate negative values which we do not care to consider
            if val[0] not in ('(', '-'):
                numtext = ''.join(filter(str.isdigit, val))
                if numtext:
                    numint = int(numtext)
                    true_int = numint*scale_factor
                    if true_int>max_num["value"]:
                        max_num["value"]=true_int
                        max_num["original_text"]=val
                        max_num["page_number"]=page_number


def get_max_number_in_pdf(file_name, model_name='en_core_web_sm'):
    max_num = {"value": -math.inf, "original_text": None, "page_number": None}
    nlp = load(model_name)
    doc = fitz.open(file_name)
    page_number = 1
    for page in doc:
        tabs = page.find_tables()
        if tabs.tables:
            for ctable in tabs.tables:
                table_data = ctable.extract()
                #note we are only checking for mentioned scales in first two rows
                #i would rather not accidentally identify a value as a scale
                #if the convention is different, this logic could be changed
                scale_factor = check_for_scale_identifiers(table_data[0])
                table_data.pop(0)
                if not scale_factor and len(table_data)>1:
                    scale_factor = check_for_scale_identifiers(table_data[1])
                    table_data.pop(0)
                if scale_factor>1:
                    update_max_with_scaled_table_val(table_data, scale_factor, page_number, max_num)

        #besides tables with scaled values, we parse the text through spacy to try to catch numbers mentioned in words anywhere
        #if you are not interested in numbers mentioned in tables, the table section (lines 62-75) could be commented out
        content = page.get_text("text")
        doc = nlp(content)
        a = doc._.numerize()
        check_update_max(a, page_number, max_num)    
        page_number+=1
    return max_num

#set to local location if it is not in current working directory
file_name = 'FY25 Air Force Working Capital Fund.pdf'
max_num_for_file = get_max_number_in_pdf(file_name)
print(max_num_for_file)
