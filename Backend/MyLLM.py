from openai import OpenAI

client = OpenAI(
    base_url = "http://localhost:1234/v1",
    api_key= "lm-studio"
)

def query_llm(prompt, m=1024):
    response = client.chat.completions.create(
        model="mistral-7b-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens = m,
        temperature = 0.4
    )

    return response.choices[0].message.content
    
    
def build_prompt(question, context_chunks):
    
    context = "\n\n".join(context_chunks[:1])[:800]

    prompt = f"""

if the question is a greeting, like Hi, Hello, Hey, Good Morning, Good Afternoon, Good Evening, Good Night, then answer politely and briefly with only a friendly greeting and tell the user to ask anything related to the resume.

else if the question is not related to the context of your resume or job description, then answer politely and briefly that it is not related to the context of your resume or job please ask something related to your resume.

Only if the question is related to the context of your resume or job description then, 

    You are an AI career assistant:

    Use the following context (resume + job description) to answer the question.

    Context:
    {context}

    Question:
    {question}

    Instructions:
    - Be clear and concise
    - If asked about improvement, give actionable suggestions, keep it short

Answer:
"""

    return prompt