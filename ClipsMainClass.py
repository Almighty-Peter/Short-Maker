size_of_captions_to_GPT = 60
distance_from_star_end = 60
distance_from_clips = 60


get_many_insted_of_threshold = True
retention_threshold = 60 # lower better

start_clip_before = 3
start_clip_after = 1
quality_of_video=8 # a multiple of 108 and 192 as this is 1/10 of 1080 by 1920 the frame of tiktok




from YouTubeAudienceRetention import getYoutubeAudienceRetention
from AiApis import textToText, textToAudio, textToImage
from TextCreators.SIENCETextCreator import SIENCE_create_text_clips
from TextCreators.MOTIVIATIONALTextCreator import MOTIVATIONAL_create_text_clips
from TextCreators.GAMINGTextCreator import GAMING_create_text_clips
from TextCreators.FUNNY_VLOGSTextCreator import FUNNY_VLOGS_create_text_clips

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/peternyman/Clips/woven-victor-430706-q3-0e3eeca05bbd.json"
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"
os.environ["IMAGEIO_FFPROBE_EXE"] = "/opt/homebrew/bin/ffprobe"
from pytube import YouTube
from google.cloud import speech_v1p1beta1 as speech
import io
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import re
import random
import json
import math
import requests
from pydub import AudioSegment
from moviepy.video.fx.all import speedx



from moviepy.editor import *
from moviepy.config import change_settings



change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})
change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/magick"})


import array
import sqlite3
from datetime import datetime


connection = sqlite3.connect('local_database.db')
cursor = connection.cursor()



cursor.execute("Drop TABLE IF EXISTS TKCuts")
connection.commit()

create_table_query = """
CREATE TABLE IF NOT EXISTS TKCuts (   
    channel TEXT,
    TKChannel TEXT,

    video_id CHAR(11), 
    start_time INT,
    end_time INT,

    event_date TEXT,
    caption TEXT,
    TK_link TEXT,

    length FLOAT,
    size_of_captions_to_GPT INT,
    position INT,
    data TEXT, 

    PRIMARY KEY( video_id, start_time, end_time)
);
"""

cursor.execute(create_table_query)
connection.commit()








class Main():
    def __init__(self, TKChannel, video_id, yt, captions_prompt, captions_sys_message, time_stamps_prompt, time_stamps_sys_message, intro_prompt, intro_sys_message, image_prompt, image_sys_message):
        temp = YouTubeTranscriptApi.get_transcript(video_id)
        self.TKChannel = TKChannel
        self.video_id = video_id
        self.yt = yt
        self.length = yt.length  
        self.get_how_many = math.floor(self.length/120)

        if self.get_how_many > 9:
            self.get_how_many = 9
        
        self.download_path = "/Users/peternyman/Downloads/"

        self.captions_prompt = captions_prompt
        self.captions_sys_message = captions_sys_message

        self.time_stamps_prompt = time_stamps_prompt
        self.time_stamps_sys_message = time_stamps_sys_message

        self.intro_prompt = intro_prompt
        self.intro_sys_message = intro_sys_message

        self.image_prompt = image_prompt
        self.image_sys_message = image_sys_message


        

    def main(self):
            self.get_captions()
            self.get_timestamps()
            self.download_video()

            for i,timeStamp in enumerate(self.timeStamps):
                self.timeStamps[i] = [timeStamp[0]-start_clip_before,timeStamp[1]+start_clip_after,timeStamp[2]]
            
    
    def get_captions(self): 
        lowAudienceRetentionData = []
        self.channel, audienceRetentionData = getYoutubeAudienceRetention(self.video_id)
        
        while True:
            smallest = [0,1000]  
            for i, retention in enumerate(audienceRetentionData):
                seconds = self.length * ((i+1)/len(audienceRetentionData))


                if seconds > distance_from_star_end and seconds < self.length-distance_from_star_end:
                    if smallest[1] > retention:

                        addData = True
                        for data in lowAudienceRetentionData:
                            if abs(data - seconds) < distance_from_clips:
                                addData = False
                                break
                        if addData:
                            smallest = [seconds,retention]
            
            if get_many_insted_of_threshold:
                if smallest[1] == 1000:
                    break
                elif len(lowAudienceRetentionData) >= self.get_how_many:
                    break
                else:
                    lowAudienceRetentionData.append(smallest[0])
                    print(f'retention:{smallest[1]}')
            else:
                if smallest[1] < retention_threshold:
                    lowAudienceRetentionData.append(smallest[0])
                    print(f'retention:{smallest[1]}')
                else:
                    break
                    
        lowAudienceRetentionCaptions = []
        transcript = YouTubeTranscriptApi.get_transcript(self.video_id)
        
        for timeStamps in lowAudienceRetentionData:
            lowAudienceRetentionCaptions.append([])
            for entry in transcript:
                    if abs(entry['start'] - timeStamps) < size_of_captions_to_GPT:

                        lowAudienceRetentionCaptions[len(lowAudienceRetentionCaptions)-1].append([entry['start'],entry['text']])
        
        captions = []
        for data in lowAudienceRetentionCaptions:
            currentMemory = ""
            for start, text in data:
                currentMemory += f'Start Time: {start}, Caption: {text}\n'
            captions.append(currentMemory)
        
        self.captions = captions
    


    def get_timestamps(self):       
            
        timeStamps = []
        for caption in self.captions:
            
            prompt = f"{self.time_stamps_prompt}{caption}"
            print(prompt)
            result = textToText(prompt,self.time_stamps_sys_message)

            pattern = r"\b\d+\.\d+\b"
            timestamps = [round(float(timestamp)) for timestamp in re.findall(pattern, result)]
            try:
                print([timestamps[-2],timestamps[-1]])
            except:
                timestamps = [round(float(time)) for time in re.findall(r'Start Time: (\d+\.\d+)', caption)]
                timestamps=[min(timestamps), max(timestamps)]

            data = {"timeStamps":{"system_message":self.time_stamps_sys_message,
                                  "prompt":prompt,
                                  "result":result}}

            timeStamps.append(([timestamps[-2],timestamps[-1], data]))
        
        self.timeStamps = timeStamps
    
    
    def download_video(self):
    
        url = f'https://www.youtube.com/watch?v={self. video_id}'
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # More flexible format selection
            'outtmpl': f'{self.download_path}{self. video_id}.%(ext)s',
            'merge_output_format': 'mp4',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    
        
    def audio_to_text(self):

        audio = AudioSegment.from_mp3("audio.mp3")
        audio = audio.set_channels(1) 
        wav_file_path = f"{self.download_path}{self.video_id}.wav"
        
        audio.export(wav_file_path, format="wav")


        sample_rate_hertz = audio.frame_rate

        client = speech.SpeechClient()


        chunk_duration_ms = 40 * 1000 
        total_duration_ms = len(audio)
        chunks = [audio[i:i + chunk_duration_ms] for i in range(0, total_duration_ms, chunk_duration_ms)]

        transcript = {}
        current_time_offset = 0.0  # To keep track of the current timestamp offset

        for i, chunk in enumerate(chunks):
            
            chunk_wav_file_path = f"{self.download_path}{self.video_id}_chunk_{i}.wav"
            chunk.export(chunk_wav_file_path, format="wav")

            with io.open(chunk_wav_file_path, 'rb') as audio_file:
                content = audio_file.read()

            recognition_audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=sample_rate_hertz,  # Use the extracted sample rate
                language_code='en-US',
                enable_word_time_offsets=True
            )

            # Use LongRunningRecognize for each chunk
            operation = client.long_running_recognize(config=config, audio=recognition_audio)
            response = operation.result(timeout=90)

            for result in response.results:
                alternative = result.alternatives[0]
                for word_info in alternative.words:
                    word = word_info.word
                    start_time_seconds = word_info.start_time.total_seconds() + current_time_offset
                    transcript[start_time_seconds] = word

            current_time_offset += len(chunk) / 1000.0  # Increment offset by the chunk duration in seconds

        return transcript

    def create_intro(self, transcript, transcriptForTiktok,start_time,end_time, data, audio):
            prompt = self.intro_prompt.replace("$$$YT_CHANNEL$$$", self.yt.author).replace("$$$CAPTION$$$", transcriptForTiktok)

            intro = textToText(prompt,self.intro_sys_message,model="gpt-4o")
            print(intro)
            data = {**data, "Intro": {"system_message": self.intro_sys_message,
                                        "prompt": prompt,
                                        "result": intro}}
            

            intro_path = textToAudio(intro)
            intro_audio = AudioFileClip(intro_path)
            audio = concatenate_audioclips([intro_audio, audio])
            content_clip = VideoFileClip(f"{self.download_path}{self.video_id}.mp4").subclip(start_time-intro_audio.duration, end_time)

            intro_audio.write_audiofile(f"audio.mp3")
            transcript2 = self.audio_to_text()

            shifted_transcript = {timestamp + intro_audio.duration: word for timestamp, word in transcript.items()}
            transcript = {**transcript2, **shifted_transcript}
            return transcript, content_clip, data, audio
    
    def get_text_between_timestamps(self, start_timestamp, end_timestamp):
        extracted_text = []
        data = YouTubeTranscriptApi.get_transcript(self.video_id)
        for entry in data:
            start = entry['start']
            end = start + entry['duration']
            

            if start >= start_timestamp and end <= end_timestamp:
                extracted_text.append(entry['text'].replace("\xa0\n","\n").replace("\xa0\xa0","\n"))
    
        return ''.join(extracted_text)
    

    def create_images_concepts(self, start_time, end_time, transcript):
        context = self.get_text_between_timestamps((start_time-60), (end_time+60))
        prompt = ""
        all_timestamps = []
        next = 0.25
        first_time = 0.0
        for i, [time, word] in enumerate(transcript.items()):
            prompt+= f"{time}: '{word}',"
            if i / len(transcript.items()) > next:
                next += 0.25
                all_timestamps.append([prompt[:-1],first_time,time+0.5])
                first_time = time
                prompt = ""
        all_timestamps.append([prompt[:-1],first_time,time])    


        all_prompts = []
        for [timestamps,first_time,last_time] in all_timestamps:
            print(f"---------------------------timestamps----------------------------{timestamps}----------------------------timestamps---------------------------")
            prompt = self.image_prompt.replace("$$$TIMESTAMPS$$$",timestamps).replace("$$$CONTEXT$$$",context)
            result = textToText(prompt,self.image_sys_message,"gpt-4o").replace("   ","").replace("- ","")
            print(f"----------------------------result---------------------------{result}----------------------------result---------------------------")

            pattern = r'```python(.*?)```'
            python_blocks = re.findall(pattern, result, re.DOTALL)
            pattern = r'start = ([\d.]+)\nduration = ([\d.]+)\nimage_prompt = "(.*?)"'

            for entry in python_blocks:
                entries = re.finditer(pattern, entry)
                for match in entries:
                    start = float(match.group(1))
                    duration = float(match.group(2))
                    prompt = match.group(3)
                    if last_time > start > first_time:
                        all_prompts.append({"start": start, "duration": duration, "image_prompt": prompt})
                        print(all_prompts[-1])

        return all_prompts
    
    def create_image_clip(self, image_prompt, start, duration):
        response = requests.get(textToImage(image_prompt))
        with open("generated_image.png", "wb") as file:
            file.write(response.content)

        image_clip = ImageClip("generated_image.png", duration=duration)

        image_clip = image_clip.set_position(('center', 'center'))
        image_clip = image_clip.set_start(start)
        return image_clip
    
        """Illustration of a brain with sections labeled to represent different 
        world views and opinions, showing the concept of social sorting."""  

        # The Above should become the bellow just like dale-3 on chat gpt app

        """An illustration of a human brain divided into sections, each labeled
        with different world views and opinions, representing the concept of
        social sorting. The brain is shown in a colorful, abstract style, with
        segments labeled with concepts like ‘political beliefs,’ ‘cultural
        values,’ ‘religion,’ ‘media influence,’ and ‘personal experiences.’ 
        Arrows or pathways connect the segments, illustrating how these aspects 
        interact and shape an individual’s worldview. The background has subtle 
        imagery of social networks or groups, symbolizing how people are grouped 
        or sorted based on shared opinions and beliefs."""

    def clip(self, start_time, end_time, data, position):

        
        frame_width = 108*quality_of_video
        frame_height = 192*quality_of_video
        frame_rate = 10


        
        clipsOutputPath = f"/Users/peternyman/Clips/Clips/YT={self.video_id}S={start_time}E={end_time}.mp4"
        print("clipsOutputPath: "+ clipsOutputPath)

        content_clip = VideoFileClip(f"{self.download_path}{self.video_id}.mp4").subclip(start_time, end_time)
        audio = content_clip.audio
        audio.write_audiofile(f"audio.mp3")

        transcript = self.audio_to_text()

        transcriptForTiktok = ""
        current_line_length = 0
        for _, word in dict(sorted(transcript.items())).items():
            word_length = len(word)
            

            if current_line_length + word_length + 1 > 30:  
                transcriptForTiktok += "\n"
                current_line_length = 0 
            

            if current_line_length > 0: 
                transcriptForTiktok += " "
                current_line_length += 1 
                
            transcriptForTiktok += word
            current_line_length += word_length

        print(transcriptForTiktok)


        if self.TKChannel == "SCIENCE" or self.TKChannel == "FUNNY VLOGS":
            transcript, content_clip, data, audio = self.create_intro(transcript, transcriptForTiktok,start_time,end_time, data, audio)


        if self.TKChannel == "MOTIVATIONAL":
            # brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot/MOTIVATIONAL') if file.endswith('mp4')])
            brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot') if file.endswith('mp4')])
            text_clips  = MOTIVATIONAL_create_text_clips(transcript, frame_width, quality_of_video)
        elif self.TKChannel == "SCIENCE":
            # brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot/SCIENCE') if file.endswith('mp4')])
            brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot') if file.endswith('mp4')])
            text_clips  = SIENCE_create_text_clips(transcript, frame_width, quality_of_video)
        elif self.TKChannel == "GAMING":
            # brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot/GAMING') if file.endswith('mp4')])
            brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot') if file.endswith('mp4')])
            text_clips  = GAMING_create_text_clips(transcript, frame_width, quality_of_video)
        elif self.TKChannel == "FUNNY VLOGS":
            # brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot/FUNNY VLOGS') if file.endswith('mp4')])
            brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot') if file.endswith('mp4')])
            text_clips  = FUNNY_VLOGS_create_text_clips(transcript, frame_width, quality_of_video)
            

        content_height = int(frame_height * 0.6)
        if self.TKChannel == "SCIENCE" or self.TKChannel == "GAMING" or self.TKChannel == "FUNNY VLOGS":
            brain_root_height = frame_height - content_height

            brain_root = f'/Users/peternyman/Clips/brainRoot/{brain_root}'
        
            brain_rootDuration = math.floor(VideoFileClip(brain_root).duration)
            brain_root_start_time = random.randrange(0,math.floor(brain_rootDuration - content_clip.duration))
            brain_root_clip = VideoFileClip(brain_root).subclip(brain_root_start_time, content_clip.duration + brain_root_start_time).resize(height=brain_root_height)
        

            content_clip = content_clip.resize(height=content_height)

            composite_clip = CompositeVideoClip([
                content_clip.set_position(('center', 'top')),
                brain_root_clip.set_position(('center', 'bottom'))
            ], size=(frame_width, frame_height))
        else:
            composite_clip = CompositeVideoClip([
                content_clip.set_position(('center', 'center')),
            ], size=(frame_width, frame_height))



        if self.TKChannel == "MOTIVATIONAL" or self.TKChannel == "SCIENCE" or self.TKChannel == "FUNNY VLOGS":
            
            all_prompts = self.create_images_concepts(start_time, end_time, transcript)
            
            image_clips = [self.create_image_clip(prompt["image_prompt"], prompt["start"], prompt["duration"]) for prompt in all_prompts]
            composite_clip = CompositeVideoClip([composite_clip] + image_clips)


        final_clips = [composite_clip] + text_clips 
        final_composite_clip = CompositeVideoClip(final_clips, size=(frame_width, frame_height))
        final_composite_clip = final_composite_clip.set_audio(audio)


        final_composite_clip = speedx(final_composite_clip, factor=1.2)
        length = final_composite_clip.duration
        final_composite_clip.write_videofile(clipsOutputPath, fps=frame_rate, codec='libx264', audio_codec='aac', verbose=True, logger='bar')
        os.remove(f"audio.mp3")
        os.remove(f"{self.download_path}{self.video_id}.wav")

        prompt = self.captions_prompt.replace("$$$YT_CHANNEL$$$", self.yt.author).replace("$$$CAPTION$$$", transcriptForTiktok)
        tkCaption = textToText(prompt,self.captions_sys_message)
        data = {**data, "Caption": {"system_message": self.captions_sys_message,
                                    "prompt": prompt,
                                    "result": tkCaption}}
        TK_link = None
        event_date = datetime.now().strftime('%Y-%m-%d')

        cursor.execute('DELETE FROM TKCuts WHERE  video_id = ? AND start_time = ? AND end_time = ?', (self.video_id,start_time,end_time))
        insert_query = """
        INSERT INTO TKCuts (
             YTChannel, TKChannel, video_id, start_time, end_time, event_date, caption, TK_link, length, size_of_captions_to_GPT, position, data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, )
        """

        cursor.execute(insert_query, (
            self.channel, 
            self.TKChannel,
            self.video_id, 
            start_time, 
            end_time, 
            event_date, 
            tkCaption, 
            TK_link, 
            length,
            size_of_captions_to_GPT, 
            position,
            json.dumps(data)
        ))
        connection.commit()


    
    













