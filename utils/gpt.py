import openai
import os
from time import time, sleep

def gpt3_embedding(content, engine='text-embedding-ada-002'):
    response = openai.Embedding.create(input=content,engine=engine)
    vector = response['data'][0]['embedding']  # this is a normal list
    return vector


def gpt_chat(messages, model="gpt-3.5-turbo", temperature=0.0, max_tokens=1024, stop=None, n=1, log=False):
    max_retry = 5
    retry = 0
    while True:
        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                n=n
            )
            gpt_response = completion.choices[0].message.content
            if log:
                filename = '%s_gpt.txt' % time()
                if not os.path.exists('gpt_logs'):
                    os.makedirs('gpt_logs')
                with open('gpt_logs/%s' % filename, 'w') as f:
                    f.write(str(messages) + '\n\n==========\n\n' + gpt_response)
            return gpt_response
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT 3.5/4 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)