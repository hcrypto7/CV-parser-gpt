import os
import asyncio
from openai import AsyncOpenAI
import json
from fpdf import FPDF
from output_file import txt_save, pdf_save



client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def main(json_string) -> None:
  
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Reassemble the following CV in Spanish with the following order:\n"+
                        "- PERSONAL DATA (name, age, marital status, nationality and current location, email, phone number, relevant years of experience)\n"+
                        "- PROFILE\n"+
                        "- SKILLS\n"+
                        "- LANGUAGES\n"+
                        "- PROFESSIONAL EXPERIENCE (write the name of the company in parentheses and give a brief summary of what the company does, specify the dates and detail well what the candidate does) (the most current job should go first and then the oldest) Put the name of the company of the professional experience in parentheses, but mention the area to which the company is dedicated.\n"+
                        "- ACADEMIC EXPERIENCE\n"+
                        "- RELEVANT COURSES OR ACTIVITIES\n"+
                        "- REFERENCES\n" + ":" + json_string,
            }
        ],
        model="gpt-3.5-turbo",
    )
    text = chat_completion.choices[0].message.content
    # print(text)
    return text


def gptProcess(text, path, index):
    json_string = json.dumps(text)
    result = asyncio.run(main(json_string))
    filename = path + '\\' + 'candidate' + str(index) + '.txt'
    txt_save(filename, result)
    filename_pdf = path + '\\' + 'candidate' + str(index) + '.pdf'
    pdf_save(filename_pdf, result)
    return result