from openai import OpenAI
from pathlib import Path


api_key=''
client = OpenAI(api_key=api_key)

def textToText(prompt,system_message,model="gpt-4o-mini"):
    completion = client.chat.completions.create(
      model=model,
      messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
      ]
    )

    return(completion.choices[0].message.content)

def get_embedding(text, model="text-embedding-3-large"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def textToAudio(prompt):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=prompt
    )
    
    audio_filename = "generated_audio.mp3"
    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(response.content)
    
    return audio_filename
