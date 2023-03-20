import os
import openai
from dotenv import load_dotenv
import PyPDF2 as pdf2

load_dotenv()

openai.api_key = os.getenv("gptKey")


def getMostCommonWord(filename):
    with open (filename, "rb") as f:
        pdf = pdf2.PdfReader(f)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        words = text.split()
        f.close()

        liste = []
        # split the words into 500 word chunks
        for i in range(0, len(words), 500):
            liste.append(words[i:i+500])
    return liste

def analyzePDF(filename):
    liste = getMostCommonWord(filename)
    listeTags = []
    for i in range(len(liste)):
        convert = " ".join(liste[i])
        p = f'''Give me the 5 most representative words of the following text:
        {convert}'''

        print(p)

        # generate the response
        response = openai.Completion.create(
            engine="davinci-instruct-beta-v3",
            prompt=p,
            temperature=.7,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["12."]
            )

        # grab our text from the repsonse
        text = response['choices'][0]['text']
        listeTags.append(text)

    return listeTags