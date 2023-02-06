import openai
import os

API_KEY = os.environ.get('OPENAI')

def run(k, q):
    # Set the API key
    openai.api_key = k

    # Generate text using the GPT-3 model
    model_engine = "text-davinci-003"
    question = q

    completions = openai.Completion.create(
        engine=model_engine,
        prompt=question,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    a = completions.choices[0].text
    print(type(a), len(a), len(completions.choices))
    
    #aa=a.replace("\n","<br />\n")
    return (a)


if __name__ == "__main__":
    
    qq1 = "python sample code which add 1 to 10"
    qq2 = "make 3 page report on south korea"
    qq3 = "대한민국을 소개해 주세요"

    question = qq2

    answer = run(API_KEY, question)
    print(answer)

'''
'''

