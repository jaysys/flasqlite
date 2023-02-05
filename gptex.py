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
    
    aa=a.replace("\n","<br />\n")
    aa=aa.replace("\t","&nbsp&nbsp&nbsp&nbsp")
    return (aa)


if __name__ == "__main__":
    
    question = "python sample code which add 1 to 10" # make 3 page technical report on IoT introduction"
    '''
    "python sample code which add 1 to 10"
    '''

    answer = run(API_KEY, question)
    print(answer)

'''

'''