size_of_captions_to_GPT = 60
distance_from_star_end = 60
distance_from_clips = 60


get_many_insted_of_threshold = True
retention_threshold = 60 # lower better

start_clip_before = 3
start_clip_after = 1
quality_of_video=8 # a multiple of 108 and 192 as this is 1/10 of 1080 by 1920 the frame of tiktok




from YouTubeAudienceRetention import getYoutubeAudienceRetention
from ChatGpt import textToText, get_embedding, textToAudio
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
from pydub import AudioSegment
from moviepy.video.fx.all import speedx
import traceback


from moviepy.editor import *
from moviepy.config import change_settings



change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/convert"})
change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/magick"})


import array
import sqlite3
from datetime import datetime


connection = sqlite3.connect('local_database.db')
cursor = connection.cursor()



create_table_query = """
CREATE TABLE IF NOT EXISTS TKCuts (
    video_id CHAR(11),  
    channel TEXT,
    start_time INT,
    end_time INT,
    event_date TEXT,
    embedding BLOB,
    caption TEXT,
    TK_link TEXT,
    brain_root CHAR(11),
    brain_root_start_time INT,
    brain_root_end_time INT,

    size_of_captions_to_GPT INT,
    distance_from_star_end INT,
    distance_from_clips INT,

    get_how_many INT,
    position INT,
    get_many_insted_of_threshold BOOLEAN,
    retention_threshold INT,

    start_clip_before INT,
    start_clip_after INT,
    quality_of_video INT,

    border_bettewn_text INT,
    max_chars_text INT,

    font_default TEXT,
    font_sized_default INT,
    color_default TEXT,
    stroke_color_default TEXT,
    stroke_width_default INT,

    font_marked TEXT,
    font_size_marked INT,
    color_marked TEXT,
    bg_color_marked TEXT,
    stroke_color_marked TEXT,
    stroke_width_marked INT, 

    what_captalazation INT,
    
    data TEXT, 

    PRIMARY KEY( video_id, start_time, end_time)
);
"""

cursor.execute(create_table_query)
connection.commit()








class Main():
    def __init__(self,  video_id, yt):
        temp = YouTubeTranscriptApi.get_transcript(video_id)
        self.video_id =  video_id
        self.yt = yt
        self.length = yt.length  
        self.get_how_many = math.floor(self.length/120)
        self.download_path = "/Users/peternyman/Downloads/"

        if self.get_how_many > 9:
            self.get_how_many = 9
        self.get_how_many = 1
        self.main()

    def main(self):
            self.get_captions()
            self.get_timestamps()
            self.download_video()

            for i,timeStamp in enumerate(self.timeStamps):

                self.timeStamps[i] = [timeStamp[0]-start_clip_before,timeStamp[1]+start_clip_after,timeStamp[2]]
            

            for position, timeStamp in enumerate(self.timeStamps):
                try:
                    
                    self.clip(timeStamp[0], timeStamp[1], timeStamp[2], position)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    traceback.print_exc()

            os.remove(self.download_path+self.video_id+".mp4")
    
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
            
        system_message = """You will receive a text with start times and captions. Your task is to identify the central theme or idea of the text that would be the most viral and provide the start and end times in the format: [start_time, end_time]. Use the provided data format and times to ensure consistency.
        
    For example, given the following data:

    Start Time: 23.121, Caption: jet. But here's the thing, I don't care about all that. Scroll down the page, and
    Start Time: 27.426, Caption: you'll find that there are true gourmet meals on board, and if I'm going to spend $30,000 on
    Start Time: 30.49, Caption: a plane ticket just to get the food, I'm going to get my money's worth.   But I think
    Start Time: 34.722, Caption: that's achievable because I see that you can order whatever you want, whenever you
    Start Time: 37.624, Caption: want. And because this is what they call a long-haul flight, check out how insane
    Start Time: 41.217, Caption: this sample menu is. This menu is almost as long as the Cheesecake Factory menu.
    Start Time: 44.847, Caption: Before we take flight, I'll remind you that we are catching up to Gordon, and I
    Start Time: 48.548, Caption: know that half of you watching aren't subscribed, so go hit that button below to
    Start Time: 51.632, Caption: help us catch Gordon. Enough talking, it's time to fly. To begin our journey, Emirates
    Start Time: 56.734, Caption: sent a car to pick me up and bring me to the airport. It even had these fancy lights

    The most viral central theme or idea might be about the gourmet meals on board and the luxurious experience, starting from 27.426 to 41.217. Thus, the output should be:

    [27.426, 41.217]

    Please proceed with the provided data."""
        

        # TODO: check if what chatgpt says actualy happens
        timeStamps = []
        for caption in self.captions:
            
            prompt = f"Identify the central theme or idea in the following text that would be the most viral, and provide the start and end times in the format: [start_time, end_time].\n\n{caption}"
            pattern = r"\b\d+\.\d+\b"
            result = textToText(prompt,system_message)
            timestamps = [round(float(timestamp)) for timestamp in re.findall(pattern, result)]
            try:
                print([timestamps[-2],timestamps[-1]])
            except:
                timestamps = [round(float(time)) for time in re.findall(r'Start Time: (\d+\.\d+)', caption)]
                timestamps=[min(timestamps), max(timestamps)]

            data = {"timeStamps":{"system_message":system_message,
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

    def random_text(self):    
        rand = random.randint(0,4)
        if rand == 0:
            """tiktok kinda"""
            max_chars_text = 18  
            border_bettewn_text = 100

            font_default="STIXGeneral-BoldItalic"
            font_sized_default=7*quality_of_video 
            color_default='white'
            stroke_color_default = "Pink"
            stroke_width_default = 0.5*quality_of_video

            font_marked="STIXGeneral-BoldItalic"
            font_size_marked=7*quality_of_video
            color_marked='black'
            bg_color_marked='Pink'
            stroke_color_marked = "white"
            stroke_width_marked = 0.5*quality_of_video


        elif rand == 1:
            """usa prety cool"""
            max_chars_text = 18  
            border_bettewn_text = 100

            font_default="Arial-Black"
            font_sized_default=9*quality_of_video 
            color_default='deepskyblue'
            stroke_color_default = "darkblue"
            stroke_width_default = 0.7*quality_of_video

            font_marked="Arial-Black"
            font_size_marked=9*quality_of_video
            color_marked='red'
            bg_color_marked='lightyellow'
            stroke_color_marked = "darkred"
            stroke_width_marked = 0.7*quality_of_video

        elif rand == 2:
            """some what cool"""
            max_chars_text = 18  
            border_bettewn_text = 100

            font_default="Impact"
            font_sized_default=9*quality_of_video 
            color_default='cyan'
            stroke_color_default = "midnightblue"
            stroke_width_default = 0.8*quality_of_video

            font_marked="Impact"
            font_size_marked=9*quality_of_video
            color_marked='magenta'
            bg_color_marked='palegoldenrod'
            stroke_color_marked = "purple"
            stroke_width_marked = 0.8*quality_of_video

        elif rand == 3:
            """red and white some what cool"""
            max_chars_text = 18  
            border_bettewn_text = 100

            font_default="Calibri-Bold"
            font_sized_default=10*quality_of_video 
            color_default='purple'

            stroke_color_default = "palegoldenrod"
            stroke_width_default = 0.5*quality_of_video

            font_marked="Calibri-BoldItalic"
            font_size_marked=10*quality_of_video
            color_marked='palegoldenrod'
            bg_color_marked='black'
            stroke_color_marked = "DarkRed"
            stroke_width_marked = 0.5*quality_of_video

        

        elif rand == 4:
            """Neon Glow"""
            max_chars_text = 14  
            border_bettewn_text = 100

            font_default="Verdana"
            font_sized_default=9*quality_of_video 
            color_default='LightPink'
            stroke_color_default = "HotPink"
            stroke_width_default = 0.5*quality_of_video

            font_marked="Verdana-Bold"
            font_size_marked=9*quality_of_video
            color_marked='aqua'
            bg_color_marked='darkslategray'
            stroke_color_marked = "cyan"
            stroke_width_marked = 0.6*quality_of_video


        self.max_chars_text = max_chars_text  
        self.border_bettewn_text = border_bettewn_text

        self.font_default=font_default
        self.font_sized_default=font_sized_default
        self.color_default=color_default
        self.stroke_color_default = stroke_color_default
        self.stroke_width_default = stroke_width_default

        self.font_marked=font_marked
        self.font_size_marked=font_size_marked
        self.color_marked=color_marked
        self.bg_color_marked=bg_color_marked
        self.stroke_color_marked = stroke_color_marked
        self.stroke_width_marked = stroke_width_marked
    

    def create_text_clips(self, transcript, frame_width, what_captalazation, delay):
        transcript_copy = transcript.copy()  
        text_clips = []
        transcriptForTiktok = []

        while len(transcript_copy) != 0:
            chunkSave = []
            chunk = ""
            transcript_list = sorted(transcript_copy.items())
            for i, (timestamp, word) in enumerate(transcript_list):
                if len(word) + len(chunk) <= self.max_chars_text + 1:
                    chunk += word + " "
                    del transcript_copy[timestamp] 
                    chunkSave.append([timestamp, word])
                else:
                    break
            
            totalForTiktok = ""
            print(f"---------------{chunkSave}----------------")
            for i, (timestampI, wordI) in enumerate(chunkSave):
                transcript_list.pop(0)
                totalForTiktok += wordI + " "
                
                
                if i < len(chunkSave) - 1:
                    next_timestamp = chunkSave[i + 1][0]
                else:
                    next_timestamp = transcript_list[0][0] if transcript_list else timestampI

                durationI = next_timestamp - timestampI
            
                word_clips = []


                for j, (timestampJ, wordJ) in enumerate(chunkSave):


                    if what_captalazation == 1:
                        wordI = wordI.upper()
                    elif what_captalazation == 2:
                        wordI = wordI.upper()
                        wordJ = wordJ.upper()
                    space_clip = TextClip(" ",font=self.font_default, fontsize=self.font_sized_default, color=self.color_default,stroke_color=self.stroke_color_default,stroke_width=self.stroke_width_default).set_start(timestampI+delay).set_duration(durationI)    
                    
                    if timestampJ == timestampI:
                        word_clip = TextClip(wordI,font=self.font_marked, fontsize=self.font_size_marked, color=self.color_marked,bg_color=self.bg_color_marked,stroke_color=self.stroke_color_marked,stroke_width=self.stroke_width_marked).set_start(timestampI+delay).set_duration(durationI)
                    else:
                        word_clip = TextClip(wordJ,font=self.font_default, fontsize=self.font_sized_default, color=self.color_default,stroke_color=self.stroke_color_default,stroke_width=self.stroke_width_default).set_start(timestampI+delay).set_duration(durationI)
                    
                    word_clips.append(word_clip)
                    word_clips.append(space_clip)

                


                cumulative_width = 0
                cumulative_height = 0
                line_height = max([clip.h for clip in word_clips])
                
                positioned_clips = []

                for clip in word_clips:
                    if cumulative_width + clip.w > frame_width-self.border_bettewn_text:
                        cumulative_width = 0
                        cumulative_height += line_height  
                    positioned_clips.append(clip.set_position((cumulative_width, cumulative_height)))
                    cumulative_width += clip.w


                final_width = frame_width-self.border_bettewn_text
                final_height = cumulative_height + line_height


                text_clip = CompositeVideoClip(positioned_clips, size=(final_width, final_height)).set_position("center")
                text_clips.append(text_clip)
            transcriptForTiktok.append(totalForTiktok)
        return text_clips, transcriptForTiktok


    def clip(self, start_time, end_time, data, position):

        
        frame_width = 108*quality_of_video
        frame_height = 192*quality_of_video
        frame_rate = 40
        duration_seconds = end_time - start_time

        
        clipsOutputPath = f"/Users/peternyman/Clips/Clips/YT={self.video_id}S={start_time}E={end_time}.mp4"
        print("clipsOutputPath: "+ clipsOutputPath)

        content_clip = VideoFileClip(f"{self.download_path}{self.video_id}.mp4").subclip(start_time, end_time)
        audio = content_clip.audio
        audio.write_audiofile(f"audio.mp3")


        transcript1 = self.audio_to_text()
        what_captalazation = random.randint(0,2)
        self.random_text()
        _, transcriptForTiktok = self.create_text_clips(transcript1, frame_width, what_captalazation, 0)
        captions = ""
        for chunk in transcriptForTiktok:
            captions += chunk + "\n"
        captions
        
        # Chat-GPT
        prompt = f"""You are tasked with crafting an irresistible introduction for a video that grips the viewer's attention and makes them eager to continue watching. Your goal is to appeal to the viewer's most basic emotions, like curiosity, excitement, or even fear of missing out. The introduction should create suspense, invoke anticipation, or stir a sense of discovery, as if watching the video will reveal something extraordinary. The introduction should feel like the start of an exciting journey where the "hunt" is the process of watching the video to uncover what it promises.

Given the following details:
- {yt.author}: Name of the YouTube channel
- {captions}: Transcript of the video

Write an engaging, emotion-driven introduction that would hook the audience and make them want to continue watching.
"""

        system_message = """
Your role is to create an emotionally charged introduction for a video based on its transcript. Your introduction should immediately engage the viewer's most primal emotions—curiosity, anticipation, excitement, or intrigue. Make the hunt for the video's content thrilling. The introduction must promise that the video holds something valuable, unexpected, or essential, making the viewer feel compelled to watch it through to the end. Use powerful, action-oriented language and vivid imagery to draw the viewer in, appealing to their deep desire for discovery and satisfaction.
"""
        
        # Claude
        prompt = f"""Your task is to write a short, compelling introduction for the following YouTube video based on the provided video transcript. The introduction should use the viewer's natural curiosity and emotions to "make the hunt fun" - that is, to hook the viewer and make them eager to continue watching the video.
Use the following information to craft your introduction:

YouTube Channel: {yt.author}
Video Transcript: {captions}

The introduction should be no more than 3-4 sentences long. It should:

Pique the viewer's interest and curiosity about the video's topic
Suggest that the video contains valuable, entertaining, or inspiring content
Compel the viewer to continue watching the video to find out more

Write the introduction in a tone and style that is appropriate for the YouTube channel and video content. Avoid giving away too many specifics that would ruin the viewer's desire to watch the full video.
"""
        
        system_message = """You are an expert at crafting engaging video introductions that leverage human psychology to "make the hunt fun" - that is, to hook viewers and make them eager to continue watching a video. Your goal is to use the provided information about the YouTube channel and video transcript to write a short, compelling introduction that will maximize the viewer's curiosity and desire to watch the full video.
When generating the introduction, consider the following:

What aspects of the video's topic or content are most likely to interest the target audience?
How can you hint at the value, entertainment, or inspiration the viewer will get from watching the full video?
What language, tone, and rhetorical techniques will most effectively grab the viewer's attention and make them want to keep watching?

The introduction should be no more than 3-4 sentences long. It should leave the viewer with a strong sense of anticipation and a compelling reason to continue watching the video.
"""

        intro = textToText(prompt,system_message,model="gpt-4o")
        
        print(intro)

        intro_path = textToAudio(intro)
        intro_audio = AudioFileClip(intro_path)
        intro_audio.write_audiofile(f"audio.mp3")
        
        data = {**data, "Intro": {"system_message": system_message,
                                    "prompt": prompt,
                                    "result": intro}}


        content_clip = VideoFileClip(f"{self.download_path}{self.video_id}.mp4").subclip(start_time-intro_audio.duration, end_time)
        text_clips, transcriptForTiktok = self.create_text_clips(transcript1, frame_width, what_captalazation, intro_audio.duration)
        transcript2 = self.audio_to_text()
        intro_text_clips, _ = self.create_text_clips(transcript2, frame_width, what_captalazation, 0)
        
        content_height = int(frame_height * 0.6)
        plot_height = frame_height - content_height

        brain_root = random.choice([file for file in os.listdir('/Users/peternyman/Clips/brainRoot') if file.endswith('mp4')])
        brain_rootCode = brain_root[:11]

        brain_root = f'/Users/peternyman/Clips/brainRoot/{brain_root}'

        
       
        
        brain_rootDuration = math.floor(VideoFileClip(brain_root).duration)
    

        brain_root_start_time = random.randrange(0,math.floor(brain_rootDuration-duration_seconds-intro_audio.duration))

        if brain_root_start_time < 0:
            print(f"ERROR --> you must emedietly delete: {brain_root}")
        

        plot_clip = VideoFileClip(brain_root).subclip(brain_root_start_time, duration_seconds + brain_root_start_time + intro_audio.duration).resize(height=plot_height)


        content_clip = content_clip.resize(height=content_height)

        composite_clip = CompositeVideoClip([
            content_clip.set_position(('center', 'top')),
            plot_clip.set_position(('center', 'bottom'))
        ], size=(frame_width, frame_height))



    
    
        intro_text_clips.extend(text_clips)

        final_clips = [composite_clip] + intro_text_clips
        final_composite_clip = CompositeVideoClip(final_clips, size=(frame_width, frame_height))

        # low intrumental music shouldant notice the musci but it shoudl be there
        # slowed/ low hum 

        # search for good clips creators on youtbe 

        final_composite_clip = final_composite_clip.set_audio(concatenate_audioclips([intro_audio, audio]))
        final_composite_clip = speedx(final_composite_clip, factor=1.5)

        final_composite_clip.write_videofile(clipsOutputPath, fps=frame_rate, codec='libx264', audio_codec='aac', verbose=True, logger='bar')
        os.remove(f"audio.mp3")
        os.remove(f"{self.download_path}{self.video_id}.wav")


        captions = ""
        for chunk in transcriptForTiktok:
            captions += chunk + "\n"
        captions



        
        prompt = f"""Given the following information:
- {yt.author}: Name of the YouTube channel
- {captions}: Transcript of the video

Create an optimized caption for the above video following these guidelines:

1. Keep it REALLY short.

2. Align the caption with the video's essence, capturing its core message or theme.

3. Break the caption into short, digestible lines using line breaks for better readability.

4. Use strategic capitalization for emphasis on key words or phrases.

5. Make the caption relatable to the target audience, considering their experiences and emotions.

6. If possible incorporate a brilliant question that encourages viewers to share their opinions and experiences in the comments.

7. Include a strong call-to-action (CTA) that prompts engagement (like, comment, share, or follow).

8. Add 8 relevant hashtags at the end to increase discoverability and reach a broader audience.

Output Format:
```
[Captions]


[3-8 relevant hashtags]
```
"""

        system_message = """You are an expert social media content creator specializing in crafting engaging and optimized captions for video content. Your task is to create the best possible caption for a given video based on provided information. Your captions should be attention-grabbing, relatable, and designed to maximize engagement and reach."""
        tkCaption = textToText(prompt,system_message)
         
        caption = tkCaption.replace("```", "")



        data = {**data, "Caption": {"system_message": system_message,
                                    "prompt": prompt,
                                    "result": tkCaption}}
        
        embedding = get_embedding(captions)
        TK_link = "NULL"
        brain_root = brain_rootCode
        brain_root_end_time = brain_root_start_time+duration_seconds
        event_date = datetime.now().strftime('%Y-%m-%d')
        embedding_bytes = array.array('d', embedding).tobytes()


        cursor.execute('DELETE FROM TKCuts WHERE  video_id = ? AND start_time = ? AND end_time = ?', (self.video_id,start_time,end_time))
        insert_query = """
        INSERT INTO TKCuts (
             video_id, channel, start_time, end_time, event_date, embedding, caption, TK_link, brain_root, brain_root_start_time, brain_root_end_time, size_of_captions_to_GPT, distance_from_star_end, distance_from_clips, get_how_many, position, get_many_insted_of_threshold, retention_threshold, start_clip_before, start_clip_after, quality_of_video, border_bettewn_text, max_chars_text, font_default, font_sized_default, color_default, stroke_color_default, stroke_width_default, font_marked, font_size_marked, color_marked, bg_color_marked, stroke_color_marked, stroke_width_marked, what_captalazation, data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(insert_query, (
            self.video_id, 
            self.channel, 
            start_time, 
            end_time, 
            event_date, 
            embedding_bytes, 
            caption, 
            TK_link, 
            brain_root,
            brain_root_start_time, 
            brain_root_end_time, 
            size_of_captions_to_GPT, 
            distance_from_star_end, 
            distance_from_clips, 
            self.get_how_many, 
            position, 
            get_many_insted_of_threshold, 
            retention_threshold, 
            start_clip_before, 
            start_clip_after, 
            quality_of_video, 
            self.border_bettewn_text, 
            self.max_chars_text, 
            self.font_default, 
            self.font_sized_default, 
            self.color_default, 
            self.stroke_color_default, 
            self.stroke_width_default, 
            self.font_marked, 
            self.font_size_marked, 
            self.color_marked, 
            self.bg_color_marked, 
            self.stroke_color_marked, 
            self.stroke_width_marked, 
            what_captalazation, 
            json.dumps(data)
        ))
        connection.commit()



cursor.execute("SELECT * FROM YTVideos ORDER BY RANDOM()")
cursor.execute('SELECT * FROM YTVideos WHERE channel IN ("MrBeast", "Zach King", "nigahiga", "David Dobrik", "WhistlinDiesel", "The Joe Rogan Experience", "NELK") ORDER BY RANDOM()')
rows = cursor.fetchall()
for (video_id1, channel1, title1, position_found1, views1, date1, search_query1, data1) in rows:
    if views1 > 100000:
        print("next")
        print(channel1)
        video_id1 = "fuhE6PYnRMc"

        try:
            print(video_id1)
            yt = YouTube(f'https://www.youtube.com/watch?v={video_id1}')
            if 10800 > yt.length > 120:

                main = Main(video_id1,yt)


        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
    
    
    #  RrjEtmeby64 KY_en3cGYVs mtWDLLtxoHY gIjJTEJ7soQ mtWDLLtxoHY
