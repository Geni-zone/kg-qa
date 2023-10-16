import json
from typing import List, Dict, Union
import PyPDF2
import openai
import json
import os
from dotenv import load_dotenv
import time
load_dotenv()

openai.api_key = os.getenv("PROF_OPENAI_API_KEY")


if __name__ == '__main__':
    start_time = time.time()

    topic = 'Nuclear Reactor'
    total_cost = {
        "gpt-3.5-turbo": 0,
        "gpt-3.5-turbo-16k": 0,
        "gpt-4": 0,
    }

    with open('nuclear-reactor/index/index_3.json', 'r') as f:
        index = json.load(f)

    pdf_file = open('textbook/(Pure)Fundamentals-of-Nuclear-Reactor-Physics2008.pdf', 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    import copy
    info = copy.deepcopy(index)

    def extract_info(word, page_num):
        print("word: ", word, "; page_num: ", page_num[:2] if len(page_num) > 2 else page_num)
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
            # print("Summarize Prompt: ", messages)
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
            # print("summary: ", summary)
            print(f"Summarize: ${gpt_price}.")

            # extract type
            model = "gpt-3.5-turbo"
            messages = [
                {"role": "system", "content": "you are master at pdf text extraction and data cleaning. You are an expert in knowledge graph and ontology."},
                {"role": "user", "content": f"Hello, can you give me some information on {word}"},
                {"role": "assistant", "content": summary},
                {"role": "user", "content": f"Thanks! So, in terms of defining an ontology for {topic}, what would be the type of the entity {word} in the topic of {topic}? Return me only the string of the type(s) of the entity, do not return me any other text."},
            ]
            # print("Initial Type Prompt: ", messages)
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

            # print(num, num.find('-'), num.count('-'))
            if str(num).find('-') != -1:
                start, end = num.split('-')
                # all_text += clean_text(pdf_reader.pages[int(start.strip()) - 1].extract_text())
                all_text += pdf_reader.pages[int(start.strip()) - 1].extract_text()

                if i < 2:
                    e_num = int(end.strip())
                    s_num = int(start.strip())
                    end_p = start.strip()
                    end_p = end_p[:-1] + end if e_num < s_num else e_num
                    # print(end, end_p)
                    # all_text += clean_text(pdf_reader.pages[int(end_p) - 1].extract_text())
                    all_text += pdf_reader.pages[int(end_p) - 1].extract_text()
                # for i in range(int(start.strip()), int(end.strip()) + 1):
                #     t = pdf_reader.pages[i - 1].extract_text()
                #     all_text += clean_text(t)
            else:
                t = pdf_reader.pages[int(num.strip()) - 1].extract_text()
                # all_text += clean_text(t)
                all_text += t
        
        summary, type = extract_summary_types(all_text)
        return summary, type

    words = []
    types = []
    i = 0
    def save():
        print(words)
        with open('nuclear-reactor/output/words_3.txt', 'w') as f:
            json.dump(words, f)
        f.close()

        print(types)
        with open('nuclear-reactor/output/types_3.txt', 'w') as f:
            json.dump(types, f)
        f.close()
        
        print(total_cost)
        with open('nuclear-reactor/output/total_cost_3.json', 'w') as f:
            json.dump(total_cost, f, indent=4)
        f.close()

        json_data = json.dumps(info, indent=4)
        with open('nuclear-reactor/output/info_3.json', 'w') as f:
            f.write(json_data)
        f.close()

        end_time = time.time()
        print(f"Time: {end_time - start_time} seconds.")
        with open('nuclear-reactor/output/time_3.json', 'w') as f:
            json.dump({"time": end_time - start_time}, f, indent=4)
        f.close()
        
    # for key and value of a dict
    for word, data in index.items():
        if i == 11: break
        if i % 10 == 0: save()
        print(f"\n{i}/{len(index)}")
        i += 1
        try:
            words += [word]
            page = data['page']
            first_type = ''
            if len(page) >= 1:
                summary, type = extract_info(word, page)
                types += [type]
                first_type = type
                info[word]['summary'] = summary
                info[word]['type'] = first_type
                info[word]['label'] = word
            l0_related_words = data['related words']

            for l0_related_word, l0_data in l0_related_words.items():
                try:
                    words += [f'{word} l0:{l0_related_word}']
                    l0_page = l0_data['page']
                    l0_type = ''
                    if len(l0_page) >= 1:
                        summary, type = extract_info(f'{word} {l0_related_word}', l0_page)
                        l0_type = f'{first_type}/{type}'
                        types += [l0_type]
                        info[word]['related words'][l0_related_word]['summary'] = summary
                        info[word]['related words'][l0_related_word]['type'] = l0_type
                        info[word]['related words'][l0_related_word]['label'] = f'{word} l0:{l0_related_word}'
                    l1_related_words = l0_data['related words']

                    for l1_related_word, l1_data in l1_related_words.items():
                        try:
                            words += [f'{word} l0:{l0_related_word} l1:{l1_related_word}']
                            l1_page = l1_data['page']
                            l1_type = ''
                            if len(l1_page) >= 1:
                                summary, type = extract_info(f'{word} {l0_related_word} {l1_related_word}', l1_page)
                                l1_type = f'{l0_type}/{type}'
                                types += [l1_type]
                                info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words']['summary'] = summary
                                info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words']['type'] = l1_type
                                info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words']['type'] = f'{word} l0:{l0_related_word} l1:{l1_related_word}'
                            l2_related_words = l1_data['related words']

                            for l2_related_word, l2_data in l2_related_words.items():
                                try: 
                                    words += [f'{word} l0:{l0_related_word} l1:{l1_related_word} l2:{l2_related_word}']
                                    l2_page = l2_data['page']
                                    l2_type = ''
                                    if len(l2_page) >= 1:
                                        summary, type = extract_info(f'{word} {l0_related_word} {l1_related_word} {l2_related_word}', l2_page)
                                        l2_type = f'{l1_type}/{type}'
                                        types += [l2_type]
                                        info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words'][l2_related_word]['summary'] = summary
                                        info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words'][l2_related_word]['type'] = l2_type
                                        info[word]['related words'][l0_related_word]['related words'][l1_related_word]['related words'][l2_related_word]['type'] = f'{word} l0:{l0_related_word} l1:{l1_related_word} l2:{l2_related_word}'
                                    l3_related_words = l2_data['related words']
                                except Exception as e:
                                    print(e)
                                    pass
                        except Exception as e:
                            print(e)
                            pass
                except Exception as e:
                    print(e)
                    pass
        except Exception as e:
            print(e)
            pass

    save()
    pdf_file.close()