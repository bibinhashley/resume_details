import spacy
import headers_para
import fitz
import json
import os
import sys
import re

'''
headers_para is a code that I found on medium that can extract pdf and diffrentiate between headings and paragraphs
in that pdf so that I could extract the headings from the pdf. It outputs as a list of sentences.
'''

'''
I couldn't extract address from resume because phone number was not in the right format in the sample pdf which I
worked on and address was madeup one. If it was an original place, I could use spacy to recognize the GPR entity
or regular expression to extract using that pattern of address and mobile number

'''


# Here am using sys.argv built in library to iterate through arguments that passed at commandline
# I tried using argparse but it wasn't successful in this case
if (sys.argv[1] == '--input' and sys.argv[3] == '--output'):
    with open(sys.argv[2], 'rb') as f:
        doc = fitz.open(sys.argv[2])
        output = sys.argv[4]


elif (sys.argv[3] == '--input' and sys.argv[1] == '--output'):
    with open(sys.argv[4], 'rb') as f:
        doc = fitz.open(sys.argv[4])
        output = sys.argv[2]


# if user didn't input '--input' or '--output' , this statment will print a help statment
else:
    print('--input <pdf path with name> --output <json ouput path with naem>')
    sys.exit()


current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, "Output")
headers = headers_para.headers(doc)

''' 
appended "End" to the end of headers_list returned from headers_para so that I could iterate through headings
and extract paragraphs between those headings. If there is no "End" heading, it will run out of index.
'''
headers_list = []
headers.append("<h2>End")


# here I extracted headings from headers_list which has "<h2>" tag infront of them which means they are headings
for header in headers:
    if header.startswith("<h2>"):
        headers_list.append(header.replace('<h2>', "").replace("|", ''))


# removing unwanted symbols in the text and converting to a string instead of list
resume_text = "".join(headers).replace("|", '').replace("_", '')
resume_text = " ".join(resume_text.split())

# I used Spacy for extracting the name
nlp = spacy.load('en_core_web_sm')
doc = nlp(resume_text)  # loading text to spacy pipeline
resume_text = re.sub(re.compile('<.*?>'), '', resume_text)


def main():

    resume['Name'] = extract_name(doc)
    resume['Email'] = extract_email(resume_text)[0]
    # resume['Mobile']=extract_mobilenumber(resume_text)
    extract_content(resume_text)

    # Here is the main output which dumps the resume dictionary and converted it to a json file with indent 2
    # It will have all the headings that I iterated through and text in between.
    with open(output, 'w') as f:
        json.dump(resume, f, indent=2)


def extract_name(doc):
    '''
     Here spacy helped me finding the entities that are Person names, it won't be accurate always, 
     but it does the job pretty easily.
    '''
    name = str([ent for ent in doc.ents if ent.label_ == "PERSON"][0])
    return name


def extract_email(resume_text):

    # Here i used regex to find the email addresses in the pdf.
    email = re.findall(r'[\w\.-]+@[\w\.-]+', resume_text)
    return email


# I didn't use this function since the given pdf has no actual mobile number
def extract_mobilenumber(resume_text):
    mobile = re.findall(
        r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', resume_text)
    return mobile


def extract_content(resume_text):
    '''
    Headers_list was the list I extracted from the output of module headers_para and iterating through that headings
    I added them to a dictionary with headers as key and text between them as values of dictionary.
    The text between them is found by using regex which could match two headings and extract the text inbetween.
    '''
    for i in range(len(headers_list)-1):
        a, b = resume_text.find(
            headers_list[i]), resume_text.find(headers_list[i+1])
        resume[headers_list[i]] = resume_text[a+len(headers_list[i]):b]
        i += 1
    return resume


if __name__ == "__main__":
    resume = {}
    resume = main()
