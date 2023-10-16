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

    topic = 'Nuclear Reactor'
    total_cost = {
        "gpt-3.5-turbo": 0,
        "gpt-3.5-turbo-16k": 0,
        "gpt-4": 0,
    }

    with open('nuclear-reactor/index.json', 'r') as f:
        index = json.load(f)

    pdf_file = open('textbook/(Pure)Fundamentals-of-Nuclear-Reactor-Physics2008.pdf', 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    import copy
    info = copy.deepcopy(index)

    def extract_info(word, page_num):
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

        def extract_summary_types(text) -> List[str]:
            # extract summary
            model = "gpt-3.5-turbo-16k"
            messages = [
                {"role": "system", "content": "you are master at pdf text extraction and data cleaning. You are an expert in knowledge graph and ontology."},
                {"role": "user", "content": f"Hello, can you give me some information on {word}"},
                {"role": "assistant", "content": text},
                {"role": "user", "content": f"Thanks! From the information you provided, what does it say about {word} in connection with {topic}? Please summarize it for me."},
            ]
            print("Summarize Prompt: ", messages)
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.25,
                max_tokens=14000,
                stop=None,
                n=1
            )
            summary = completion["choices"][0]["message"]["content"]
            gpt_price = completion['usage']['prompt_tokens'] * 0.000003 + completion['usage']['completion_tokens'] * 0.000004
            total_cost["gpt-3.5-turbo-16k"] += gpt_price
            print("summary: ", summary)
            print(f"Summarize: ${gpt_price}.")

            # extract type
            model = "gpt-3.5-turbo"
            messages = [
                {"role": "system", "content": "you are master at pdf text extraction and data cleaning. You are an expert in knowledge graph and ontology."},
                {"role": "user", "content": f"Hello, can you give me some information on {word}"},
                {"role": "assistant", "content": summary},
                {"role": "user", "content": f"Thanks! So, in terms of defining an ontology for {topic}, what would be the type of the entity {word} in the topic of {topic}? Return me only the string of the type(s) of the entity, do not return me any other text."},
            ]
            print("Initial Type Prompt: ", messages)
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.10,
                max_tokens=2200,
                stop=None,
                n=1
            )
            initial_type = completion["choices"][0]["message"]["content"]
            gpt_price = completion['usage']['prompt_tokens'] * 0.0000015 + completion['usage']['completion_tokens'] * 0.000002
            total_cost["gpt-3.5-turbo"] += gpt_price
            print(f"Initial Type: ${gpt_price}.")

            messages.append({"role": "assistant", "content": initial_type})
            messages.append({"role": "user", "content": "Return me only the string for the type of the entity."})
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=2200,
                stop=None,
                n=1
            )
            type = completion["choices"][0]["message"]["content"]
            gpt_price = completion['usage']['prompt_tokens'] * 0.0000015 + completion['usage']['completion_tokens'] * 0.000002
            total_cost["gpt-3.5-turbo"] += gpt_price
            print(f"Type: ${gpt_price}.")

            return [summary, type]

        all_text = ''
        i = 0
        for num in page_num:
            if i == 2: break
            i += 1

            print(num, num.find('-'), num.count('-'))
            if str(num).find('-') != -1:
                start, end = num.split('-')
                all_text += clean_text(pdf_reader.pages[int(start.strip()) - 1].extract_text())

                if i < 2:
                    end_p = start.strip()
                    end_p = end_p[:-1] + end
                    print(end, end_p)
                    all_text += clean_text(pdf_reader.pages[int(end_p) - 1].extract_text())
                # for i in range(int(start.strip()), int(end.strip()) + 1):
                #     t = pdf_reader.pages[i - 1].extract_text()
                #     all_text += clean_text(t)
            else:
                t = pdf_reader.pages[int(num.strip()) - 1].extract_text()
                all_text += clean_text(t)
        
        summary, type = extract_summary_types(all_text)
        return summary, type

    words = []
    i = 0
    # for key and value of a dict
    for word, data in index.items():
        if i == 1: break

        i += 1
        words += [word]
        page = data['page']
        if len(page) >= 1:
            summary, type = extract_info(word, page)
            info[word]['summary'] = summary
            info[word]['type'] = type
        l0_related_words = data['related words']

        for l0_related_word, l0_data in l0_related_words.items():
            words += [f'{word} l0:{l0_related_word}']
            page += l0_data['page']
            if len(page) >= 1:
                summary, type = extract_info(word, page)
                info[word]['related words'][l0_related_word]['summary'] = summary
                info[word]['related words'][l0_related_word]['type'] = type
            l1_related_words = l0_data['related words']

            for l1_related_word, l1_data in l1_related_words.items():
                words += [f'{word} l0:{l0_related_word} l1:{l1_related_word}']
                page += l1_data['page']
                if len(page) >= 1:
                    summary, type = extract_info(word, page)
                    info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words']['summary'] = summary
                    info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words']['type'] = type
                l2_related_words = l1_data['related words']

                for l2_related_word, l2_data in l2_related_words.items():
                    words += [f'{word} l0:{l0_related_word} l1:{l1_related_word} l2:{l2_related_word}']
                    page += l2_data['page']
                    if len(page) >= 1:
                        summary, type = extract_info(word, page)
                        info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words'][l2_related_word]['summary'] = summary
                        info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words'][l2_related_word]['type'] = type
                    l3_related_words = l2_data['related words']

    print(words)
    with open('nuclear-reactor/words.txt', 'w') as f:
        json.dump(words, f)
    f.close()
    
    print(total_cost)
    with open('nuclear-reactor/total_cost.json', 'w') as f:
        json.dump(total_cost, f, indent=4)
    f.close()

    json_data = json.dumps(info, indent=4)
    with open('nuclear-reactor/info.json', 'w') as f:
        f.write(json_data)

    pdf_file.close()