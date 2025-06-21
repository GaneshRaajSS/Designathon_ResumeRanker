import os
import numpy as np
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")

async def get_embedding(text: str):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        encoding_format="float"
    )
    return response.data[0].embedding

async def gpt_score_resume(jd, profile):
    messages = [
        {"role": "system", "content": "You are a resume screening assistant. Score how well the resume matches the job description (0–100)."},
        {"role": "user", "content": f"Job Description:\nTitle: {jd.title}\nSkills: {jd.skills}\nExperience: {jd.experience}\nDescription: {jd.description}\n\nCandidate Profile:\nName: {profile.name}\nSkills: {profile.skills}\nExperience: {profile.experience}\nResume Text:\n{profile.resume_text}"}
    ]
    res = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0.3
    )
    return res.choices[0].message.content
