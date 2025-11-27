from pypdf import PdfReader

print("path to file:")
pdf_file = rf"{input('')}"
print("output file name:")
output_name = rf"{input('')}"

# TO-DO: define output folder instead of just file name, improve image destination
# and extraction. 

class pdf_reader:
    
    def __init__(self, pdf_file) -> None:
        self.pdf_file = PdfReader(pdf_file)
        self.pages = self.pdf_file.pages
        self.num_pages = len(self.pages)
        self.text = ""
        

    def extract_text(self):
        
        print("paginas")
        pg_ini, pg_final = int(input()), int(input())
        with open(f"{output_name}.md", "w", encoding="utf-8") as file:
            for page in self.pages[pg_ini: pg_final]:
                file.write(f'{page.extract_text()}+\n')
            print(f"Text extraction complete. Check '{output_name}.md'.")
    
    def extract_images(self):
        # TO-DO Define 
        for page in self.pages:
            for count, image_file_object in enumerate(page.images):
                with open(str(count) + image_file_object.name, "wb") as fp:
                    fp.write(image_file_object.data)


if __name__=='__main__':
    pdf = pdf_reader(pdf_file)
    # pdf.extract_text()
    pdf.extract_images()