captions_prompt = f"""Given the following information:
- $$$YT_CHANNEL$$$: Name of the YouTube channel
- $$$CAPTION$$$: Transcript of the video

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


captions_sys_message = """You are an expert social media content creator specializing in crafting engaging and optimized captions for video content. Your task is to create the best possible caption for a given video based on provided information. Your captions should be attention-grabbing, relatable, and designed to maximize engagement and reach."""


time_stamps_sys_message = """You will receive a text with start times and captions. Your task is to identify the central theme or idea of the text that would be the most viral and provide the start and end times in the format: [start_time, end_time]. Use the provided data format and times to ensure consistency.
        
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

time_stamps_prompt = "Identify the central theme or idea in the following text that would be the most viral, and provide the start and end times in the format: [start_time, end_time].\n\n"



# Chat-GPT
intro_prompt = f"""You are tasked with crafting an irresistible introduction for a video that grips the viewer's attention and makes them eager to continue watching. Your goal is to appeal to the viewer's most basic emotions, like curiosity, excitement, or even fear of missing out. The introduction should create suspense, invoke anticipation, or stir a sense of discovery, as if watching the video will reveal something extraordinary. The introduction should feel like the start of an exciting journey where the "hunt" is the process of watching the video to uncover what it promises.

Given the following details:
- $$$YT_CHANNEL$$$: Name of the YouTube channel
- $$$CAPTION$$$: Transcript of the video

Write an engaging, emotion-driven introduction that would hook the audience and make them want to continue watching.
"""

intro_sys_message = """
Your role is to create an emotionally charged introduction for a video based on its transcript. Your introduction should immediately engage the viewer's most primal emotions—curiosity, anticipation, excitement, or intrigue. Make the hunt for the video's content thrilling. The introduction must promise that the video holds something valuable, unexpected, or essential, making the viewer feel compelled to watch it through to the end. Use powerful, action-oriented language and vivid imagery to draw the viewer in, appealing to their deep desire for discovery and satisfaction.
"""

# Claude
intro_prompt = f"""Your task is to write a short, compelling introduction for the following YouTube video based on the provided video transcript. The introduction should use the viewer's natural curiosity and emotions to "make the hunt fun" - that is, to hook the viewer and make them eager to continue watching the video.
Use the following information to craft your introduction:

YouTube Channel: $$$YT_CHANNEL$$$
Video Transcript: $$$CAPTION$$$

The introduction should be no more than 3-4 sentences long. It should:

Pique the viewer's interest and curiosity about the video's topic
Suggest that the video contains valuable, entertaining, or inspiring content
Compel the viewer to continue watching the video to find out more

Write the introduction in a tone and style that is appropriate for the YouTube channel and video content. Avoid giving away too many specifics that would ruin the viewer's desire to watch the full video.
"""

intro_sys_message = """You are an expert at crafting engaging video introductions that leverage human psychology to "make the hunt fun" - that is, to hook viewers and make them eager to continue watching a video. Your goal is to use the provided information about the YouTube channel and video transcript to write a short, compelling introduction that will maximize the viewer's curiosity and desire to watch the full video.
When generating the introduction, consider the following:

What aspects of the video's topic or content are most likely to interest the target audience?
How can you hint at the value, entertainment, or inspiration the viewer will get from watching the full video?
What language, tone, and rhetorical techniques will most effectively grab the viewer's attention and make them want to keep watching?

The introduction should be no more than 3-4 sentences long. It should leave the viewer with a strong sense of anticipation and a compelling reason to continue watching the video.
"""


import sys
sys.path.append('/Users/peternyman/Documents/GitHub/Short-Maker')
from ClipsMainClass import Main
import os
import sqlite3
from pytube import YouTube
import traceback



connection = sqlite3.connect('local_database.db')
cursor = connection.cursor()


cursor.execute('SELECT * FROM YTVideos WHERE channel IN ("MrBeast", "Zach King", "nigahiga", "David Dobrik", "WhistlinDiesel", "The Joe Rogan Experience", "NELK") ORDER BY RANDOM()')
rows = cursor.fetchall()
for (video_id1, channel1, title1, position_found1, views1, date1, search_query1, data1) in rows:
    if views1 > 100000:
        print("next")
        print(channel1)

        try:
            print(video_id1)
            yt = YouTube(f'https://www.youtube.com/watch?v={video_id1}')
            if 10800 > yt.length > 120:

                main = Main("GAMING", video_id1,yt,captions_prompt, captions_sys_message, time_stamps_prompt, time_stamps_sys_message, intro_prompt, intro_sys_message, "", "")
                main.main()

                try:
                    for position, timeStamp in enumerate(main.timeStamps): 
                        main.clip(timeStamp[0], timeStamp[1], timeStamp[2], position)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    traceback.print_exc()

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
        finally:
            os.remove(f"/Users/peternyman/Downloads/{video_id1}.mp4")
    
    


