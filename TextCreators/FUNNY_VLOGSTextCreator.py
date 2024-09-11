import random
from moviepy.editor import *



def random_text(quality_of_video):    
    what_captalazation = random.randint(0,2)
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

    return (what_captalazation, max_chars_text, border_bettewn_text,
        font_default, font_sized_default, color_default, stroke_color_default, stroke_width_default,
        font_marked, font_size_marked, color_marked, bg_color_marked, stroke_color_marked, stroke_width_marked)



def FUNNY_VLOGS_create_text_clips(transcript, frame_width, quality_of_video):
    (what_captalazation, max_chars_text, border_bettewn_text,
        font_default, font_sized_default, color_default, stroke_color_default, stroke_width_default,
        font_marked, font_size_marked, color_marked, bg_color_marked, stroke_color_marked, stroke_width_marked) = random_text(quality_of_video)
    transcript_copy = transcript.copy()  
    text_clips = []


    while len(transcript_copy) != 0:
        chunkSave = []
        chunk = ""
        transcript_list = sorted(transcript_copy.items())
        for i, (timestamp, word) in enumerate(transcript_list):
            if len(word) + len(chunk) <= max_chars_text + 1:
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
                space_clip = TextClip(" ",font=font_default, fontsize=font_sized_default, color=color_default,stroke_color=stroke_color_default,stroke_width=stroke_width_default).set_start(timestampI).set_duration(durationI)    
                
                if timestampJ == timestampI:
                    word_clip = TextClip(wordI,font=font_marked, fontsize=font_size_marked, color=color_marked,bg_color=bg_color_marked,stroke_color=stroke_color_marked,stroke_width=stroke_width_marked).set_start(timestampI).set_duration(durationI)
                else:
                    word_clip = TextClip(wordJ,font=font_default, fontsize=font_sized_default, color=color_default,stroke_color=stroke_color_default,stroke_width=stroke_width_default).set_start(timestampI).set_duration(durationI)
                
                word_clips.append(word_clip)
                word_clips.append(space_clip)

            


            cumulative_width = 0
            cumulative_height = 0
            line_height = max([clip.h for clip in word_clips])
            
            positioned_clips = []

            for clip in word_clips:
                if cumulative_width + clip.w > frame_width-border_bettewn_text:
                    cumulative_width = 0
                    cumulative_height += line_height  
                positioned_clips.append(clip.set_position((cumulative_width, cumulative_height)))
                cumulative_width += clip.w


            final_width = frame_width-border_bettewn_text
            final_height = cumulative_height + line_height


            text_clip = CompositeVideoClip(positioned_clips, size=(final_width, final_height)).set_position("center")
            text_clips.append(text_clip)

    return text_clips


