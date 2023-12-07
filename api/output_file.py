import json
from fpdf import FPDF
import os

def txt_save(filename, text):
    with open(filename, 'w', encoding='utf-8') as a:
        a.write(text)




def pdf_save(filename, text):
    # save FPDF() class into a 
    # variable pdf
    pdf = FPDF()
    
    # Add a page
    pdf.add_page()
    
    # set style and size of font 
    # that you want in the pdf
    pdf.set_font("Arial", size = 15)
    
    # create a cell
    pdf.cell(200, 10, txt = "CV", 
            ln = 1, align = 'C')
    pdf.multi_cell(200, 10, txt = text, align = 'L')
    

    # save the pdf with name .pdf
    pdf.output(filename).encode('utf-8') 