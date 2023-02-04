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
    return (a)


if __name__ == "__main__":
    
    question = "show me how to code for me to add 1 to 10 in python"

    answer = run(API_KEY, question)
    print(answer)

    