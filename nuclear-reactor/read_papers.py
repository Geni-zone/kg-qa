import json
from typing import List, Dict, Union
import PyPDF2
import openai
import json
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("PROF_OPENAI_API_KEY")


if __name__ == '__main__':
    total_cost = {
        "gpt-3.5-turbo": 0,
        "gpt-3.5-turbo-16k": 0,
        "gpt-4": 0,
    }

    def clean_text(text) -> str:
        system_prompt : str = "you are master at pdf text extraction and data cleaning. You are an expert in knowledge graph and ontology."
        prompt : str = f"Here is a piece of data from a pdf extractor, can you clean the data for me and return me a cleaner version of the text:\n\n{text}"

        model = "gpt-3.5-turbo"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.85,
            max_tokens=1800,
            stop=None,
            n=1
        )
        result = completion["choices"][0]["message"]["content"]
        gpt_price = completion['usage']['prompt_tokens'] * 0.0000015 + completion['usage']['completion_tokens'] * 0.000002
        total_cost["gpt-3.5-turbo"] += gpt_price
        print(f"Text Cleaning: ${gpt_price}.")

        return result

    def read_papers(directory_path: str) -> Dict[str, Dict[str, Union[str, List[str]]]]:
        papers = {}
        filenames = os.listdir(directory_path)
        # filenames = filenames[:3]
        i = 0
        for filename in filenames:
            print(f'{i} / {len(filenames) - 1}')
            i += 1
            if os.path.splitext(filename)[1] == '.pdf':
                with open(os.path.join(directory_path, filename), 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    pages = [pdf_reader.pages[i].extract_text() for i in range(len(pdf_reader.pages))]
                    papers[filename] = pages
        return papers
    dir_path = 'paper/ANE/volume_192_november_2023'
    papers = read_papers(dir_path)
    # dump papers to json
    with open(f'{dir_path}/papers.json', 'w') as f:
        json.dump(papers, f, indent=4)
    
    print(total_cost)
    
