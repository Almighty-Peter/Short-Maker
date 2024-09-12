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


image_sys_message = """You are tasked with evaluating timestamps and context from a video to determine if adding an image at any specific point would enhance the viewer's experience. Your primary goal is to suggest only images that improve the overall content without distracting from the video’s core message. Remember, the video aims to showcase something cool, so images should not take attention away from the visual content.

Consider the provided timestamps carefully. If you find a point where a brief image would complement the video's flow, respond with the following format:

```python
start = [timestamp]
duration = [duration]
image_prompt = "[detailed description of the image]"
```

Be conservative in your suggestions. If no image is needed, you may decide not to include one at all. Each image should only appear for a short time to keep viewer engagement high."""

image_prompt = """You have been provided with specific timestamps and the video context. Your task is to review these timestamps and the entire context to assess if adding an image at any point would enhance the video without detracting from its visual appeal. Remember, the video is meant to showcase something cool, so images should be used sparingly and only if they genuinely add value.

The timestamps:
```
$$$TIMESTAMPS$$$
```

The context:
```
$$$CONTEXT$$$
```

If you find a point where an image could be useful, respond in this format:
```python
start = [timestamp]
duration = [duration]
image_prompt = "[detailed description of the image]"
```

If you find multiple points that require different images, simply rewrite the format for each one.

If no image is needed, no suggestion is necessary. Keep image duration short to maintain viewer engagement."""


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

                main = Main("MOTIVATIONAL", video_id1,yt,captions_prompt, captions_sys_message, time_stamps_prompt, time_stamps_sys_message, "", "", image_prompt, image_sys_message)
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
    
    


