#!/usr/bin/env python3
"""
ugc_avatar_studio.py

A high-fidelity 2D geometric animation studio replicating the Behance aesthetic.
Features corrected layering, random idle looking, animated speech, and dynamic gaze.
Specifically refined male1 with rectangular jaw and blush.
"""

import argparse
import math
import numpy as np
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict

# ============================================================
# Presets
# ============================================================

@dataclass
class CharacterSpec:
    bg_color: Tuple[int, int, int]
    shirt_color: Tuple[int, int, int]
    skin_color: Tuple[int, int, int]
    hair_color: Tuple[int, int, int]
    ear_color: Tuple[int, int, int]
    bridge_color: Tuple[int, int, int]
    glasses_style: str # 'round', 'rect', 'none'
    hair_style: str # 'pompadour', 'bob', 'straight'
    head_w: int = 320
    head_h: int = 480
    head_r: int = 160
    has_beard: bool = False
    has_bun: bool = False
    has_paint: bool = False
    has_tribal_eyes: bool = False
    nose_color: Optional[Tuple[int, int, int]] = None

PRESETS = {
    "male1": CharacterSpec(
        bg_color=(18, 140, 90),    # Emerald
        shirt_color=(242, 142, 61), # Orange
        skin_color=(253, 245, 230),  # Cream
        hair_color=(75, 44, 32),      # Dark Brown
        ear_color=(230, 81, 0),      # Orange Ear
        bridge_color=(230, 81, 0),    # Orange Bridge
        hair_style="pompadour",
        head_r=40, # RECTANGULAR JAW
        has_beard=True,
        glasses_style="round",
        nose_color=(230, 81, 0)
    ),
    "male2": CharacterSpec(
        bg_color=(45, 58, 94),     # Deep Blue
        shirt_color=(229, 57, 53),  # Red
        skin_color=(253, 245, 230),
        hair_color=(253, 216, 53),  # Blonde
        ear_color=(253, 245, 230),   # Skin Ear
        bridge_color=(0, 0, 0),      # Black Bridge
        hair_style="pompadour",
        has_beard=False,
        glasses_style="none",
        nose_color=(230, 81, 0)
    ),
    "female1": CharacterSpec(
        bg_color=(26, 38, 45),     # Dark Slate
        shirt_color=(150, 210, 60), # Bright Green
        skin_color=(253, 245, 230),
        hair_color=(180, 70, 40),   # Red/Orange
        ear_color=(253, 245, 230),   # Skin Ear
        bridge_color=(0, 0, 0),      # Black Bridge
        hair_style="bob",
        glasses_style="round",
        nose_color=(210, 60, 40)
    ),
    "female2": CharacterSpec(
        bg_color=(29, 131, 140),   # Teal
        shirt_color=(103, 172, 40), # Green
        skin_color=(255, 243, 227), # Pale Cream
        hair_color=(255, 145, 45),  # Bright Orange
        ear_color=(255, 210, 190),   # Skin Ear
        bridge_color=(0, 0, 0),
        hair_style="straight",
        head_h=420, 
        has_paint=True,
        has_tribal_eyes=True,
        glasses_style="none",
        nose_color=(255, 120, 40)
    )
}

# ============================================================
# Utilities
# ============================================================

def get_pill_polygon(x, y, w, h, r, res=24):
    r = min(r, w/2, h/2)
    points = []
    for a in np.linspace(-math.pi/2, 0, res):
        points.append((x + w/2 - r + r*math.cos(a), y - h/2 + r + r*math.sin(a)))
    for a in np.linspace(0, math.pi/2, res):
        points.append((x + w/2 - r + r*math.cos(a), y + h/2 - r + r*math.sin(a)))
    for a in np.linspace(math.pi/2, math.pi, res):
        points.append((x - w/2 + r + r*math.cos(a), y + h/2 - r + r*math.sin(a)))
    for a in np.linspace(math.pi, 3*math.pi/2, res):
        points.append((x - w/2 + r + r*math.cos(a), y - h/2 + r + r*math.sin(a)))
    return points

def rotate_point(point, center, angle):
    px, py = point
    cx, cy = center
    qx = cx + math.cos(angle) * (px - cx) - math.sin(angle) * (py - cy)
    qy = cy + math.sin(angle) * (px - cx) + math.cos(angle) * (py - cy)
    return (qx, qy)

# ============================================================
# Renderer
# ============================================================

class GeometricStudio:
    def __init__(self, width=1080, height=1080):
        self.w, self.h = width, height
        self.cx, self.cy = width // 2, height // 2
        
    def render_frame(self, t, spec: CharacterSpec, speech_energy=0.0):
        ss = 2
        cx, cy = self.cx * ss, self.cy * ss
        
        # 1. Animation Parameters
        march_freq = 2.0
        bounce = 1.0 - abs(math.cos(math.pi * march_freq * t))
        y_off = 35.0 * ss * bounce
        tilt = 0.05 * math.sin(math.pi * march_freq * t)
        
        # Head Look Movement (Random swaying)
        look_x = (15.0 * math.sin(t * 1.5) + 10.0 * math.cos(t * 0.7)) * ss
        look_y = (10.0 * math.cos(t * 2.1) + 5.0 * math.sin(t * 1.1)) * ss
        
        # Gaze Direction (Pupil random looking)
        gaze_x = 12.0 * ss * math.sin(t * 4.1)
        gaze_y = 6.0 * ss * math.cos(t * 2.3)
        
        # Blink Physics
        blink_val = 1.0
        if (t % 3.0) > 2.85: blink_val = 0.0
        
        # Speech Physics
        speech_m = speech_energy + 0.1 * abs(math.sin(t * 15))
        
        img = Image.new("RGBA", (self.w * ss, self.h * ss), spec.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Background Circle
        draw.ellipse((cx-485*ss, cy-485*ss, cx+485*ss, cy+485*ss), outline=(255,255,255), width=3*ss)

        # Head Anchor
        head_x, head_y = cx + look_x, cy + y_off + look_y
        head_w, head_h = spec.head_w * ss, spec.head_h * ss
        head_r = spec.head_r * ss
        pivot = (cx, cy + 300*ss)

        # 1. Back Hair
        hair_tilt = tilt * 1.1
        if spec.hair_style == "straight":
            hair_pts = get_pill_polygon(head_x, head_y + 120*ss, head_w + 20*ss, 580*ss, 80*ss)
            hair_pts = [rotate_point(p, pivot, hair_tilt) for p in hair_pts]
            draw.polygon(hair_pts, fill=spec.hair_color)
        elif spec.hair_style == "bob":
            hair_pts = get_pill_polygon(head_x, head_y + 80*ss, 480*ss, 400*ss, 200*ss)
            hair_pts = [rotate_point(p, pivot, hair_tilt) for p in hair_pts]
            draw.polygon(hair_pts, fill=spec.hair_color)

        # 2. Body
        body_y = cy + 620*ss + (y_off * 0.4)
        body_pts = get_pill_polygon(cx, body_y, 820*ss, 550*ss, 200*ss)
        draw.polygon(body_pts, fill=spec.shirt_color)
        
        # 3. Neck
        neck_top = head_y + 120*ss
        neck_bottom = body_y - 120*ss
        draw.rectangle((head_x-40*ss, neck_top, head_x+40*ss, neck_bottom), fill=spec.skin_color)
        if spec.has_paint:
            draw.rectangle((head_x-40*ss, neck_top + 60*ss, head_x+40*ss, neck_top + 100*ss), fill=(255, 120, 40))

        # 4. Ears
        ear_r = 35*ss
        for side in [-1, 1]:
            ex, ey = head_x + side * (head_w/2), head_y - 20*ss
            ex, ey = rotate_point((ex, ey), pivot, tilt)
            draw.ellipse((ex-ear_r, ey-ear_r, ex+ear_r, ey+ear_r), fill=spec.ear_color)

        # 5. Face Base
        face_pts = get_pill_polygon(head_x, head_y, head_w, head_h, head_r)
        face_pts = [rotate_point(p, pivot, tilt) for p in face_pts]
        draw.polygon(face_pts, fill=spec.skin_color)

        # 6. Beard & Blush
        if spec.has_beard:
            beard_y = head_y + 180*ss
            beard_pts = get_pill_polygon(head_x, beard_y, head_w, 140*ss, 40*ss)
            beard_pts = [rotate_point(p, pivot, tilt) for p in beard_pts]
            draw.polygon(beard_pts, fill=spec.hair_color)
            # Blush
            blush_y = head_y + 80*ss
            for side in [-1, 1]:
                bx, by = head_x + side * 110*ss, blush_y
                bx, by = rotate_point((bx, by), pivot, tilt)
                br = 30*ss
                draw.ellipse((bx-br, by-br, bx+br, by+br), fill=(255, 160, 170, 180)) # Vibrant pink

        # 7. Face Paint
        if spec.has_paint:
            paint_color = (175, 230, 245)
            for side in [-1, 1]:
                px, py = head_x + side * 105*ss, head_y + 60*ss
                px, py = rotate_point((px, py), pivot, tilt)
                draw.rectangle((px-45*ss, py-12*ss, px+45*ss, py+12*ss), fill=paint_color)

        # 8. Front Hair
        if spec.hair_style == "straight":
            bang_y = head_y - 180*ss
            bang_pts = get_pill_polygon(head_x, bang_y, head_w + 10*ss, 240*ss, 110*ss)
            bang_pts = [rotate_point(p, pivot, tilt) for p in bang_pts]
            draw.polygon(bang_pts, fill=spec.hair_color)
            notch = [rotate_point((head_x-105*ss, head_y-130*ss), pivot, tilt),
                     rotate_point((head_x-70*ss, head_y-130*ss), pivot, tilt),
                     rotate_point((head_x-105*ss, head_y-70*ss), pivot, tilt)]
            draw.polygon(notch, fill=spec.skin_color)
        elif spec.hair_style == "bob":
            bang_y = head_y - 180*ss
            bang_pts = get_pill_polygon(head_x, bang_y, head_w + 40*ss, 200*ss, 100*ss)
            bang_pts = [rotate_point(p, pivot, tilt) for p in bang_pts]
            draw.polygon(bang_pts, fill=spec.hair_color)
        elif spec.hair_style == "pompadour":
            h_y = head_y - 210*ss
            h1 = get_pill_polygon(head_x-60*ss, h_y, 320*ss, 260*ss, 110*ss)
            h2 = get_pill_polygon(head_x+160*ss, h_y+70*ss, 180*ss, 180*ss, 90*ss)
            for h in [h1, h2]:
                hp = [rotate_point(p, pivot, tilt) for p in h]
                draw.polygon(hp, fill=spec.hair_color)

        # 9. Eyes & Gaze
        eye_y = head_y - 40*ss
        if spec.has_tribal_eyes:
            ew, eh = 100*ss, 50*ss
            for side in [-1, 1]:
                ex, ey = head_x + side * 90*ss, eye_y
                etilt = tilt - side * 0.25
                epts = get_pill_polygon(ex, ey, ew, eh, 25*ss)
                epts = [rotate_point(p, pivot, tilt) for p in epts]
                epts = [rotate_point(p, rotate_point((ex, ey), pivot, tilt), etilt) for p in epts]
                if blink_val > 0.1:
                    draw.polygon(epts, fill=(255,255,255))
                    px, py = rotate_point((ex + gaze_x * 0.4, ey + gaze_y * 0.4), pivot, tilt)
                    draw.ellipse((px-14*ss, py-14*ss, px+14*ss, py+14*ss), fill=(0, 210, 255))
                else:
                    draw.line([rotate_point((ex-40*ss, ey), pivot, tilt), rotate_point((ex+40*ss, ey), pivot, tilt)], fill=(0,0,0), width=4*ss)
                # Brow
                bx, by = ex, ey - (45*ss if blink_val > 0.1 else 25*ss)
                if side == -1:
                    draw.line([rotate_point((bx-30*ss, by+15*ss), pivot, tilt), rotate_point((bx+30*ss, by-15*ss), pivot, tilt)], fill=(255,120,40), width=8*ss)
                else:
                    draw.line([rotate_point((bx-30*ss, by-15*ss), pivot, tilt), rotate_point((bx+30*ss, by+15*ss), pivot, tilt)], fill=(255,120,40), width=8*ss)
        else:
            # Standard Eyes
            for side in [-1, 1]:
                ex, ey = head_x + side * 100*ss, eye_y
                ewpts = get_pill_polygon(ex, ey, 60*ss, 40*ss, 20*ss)
                ewpts = [rotate_point(p, pivot, tilt) for p in ewpts]
                if blink_val > 0.1:
                    draw.polygon(ewpts, fill=(255,255,255))
                    px, py = rotate_point((ex + gaze_x, ey + gaze_y), pivot, tilt)
                    draw.ellipse((px-12*ss, py-16*ss, px+12*ss, py+16*ss), fill=(0,0,0))
                else:
                    draw.line([rotate_point((ex-30*ss, ey), pivot, tilt), rotate_point((ex+30*ss, ey), pivot, tilt)], fill=(0,0,0), width=6*ss)
                # Brow
                bx, by = head_x + side * 100*ss, eye_y - (75*ss if blink_val > 0.1 else 45*ss)
                draw.line([rotate_point((bx-30*ss, by), pivot, tilt), rotate_point((bx+30*ss, by), pivot, tilt)], fill=(0,0,0), width=6*ss)

        # 10. Glasses
        if spec.glasses_style != "none":
            gr = (head_w * 0.45) / 2
            for side in [-1, 1]:
                gx, gy = head_x + side * 100*ss, eye_y
                gx, gy = rotate_point((gx, gy), pivot, tilt)
                draw.ellipse((gx-gr, gy-gr, gx+gr, gy+gr), outline=(0,0,0), width=8*ss)
            draw.line([rotate_point((head_x-30*ss, eye_y-40*ss), pivot, tilt), rotate_point((head_x+30*ss, eye_y-40*ss), pivot, tilt)], fill=spec.bridge_color, width=8*ss)

        # 11. Mouth
        mouth_y = head_y + 120*ss
        if spec.has_paint: mouth_y = head_y + 180*ss
        mw, mh = 40*ss + 20*ss * speech_m, 5*ss + 40*ss * speech_m
        mx, my = rotate_point((head_x, mouth_y), pivot, tilt)
        if speech_m < 0.2:
            draw.line([rotate_point((head_x-30*ss, mouth_y), pivot, tilt), rotate_point((head_x+30*ss, mouth_y), pivot, tilt)], fill=(0,0,0), width=6*ss)
        else:
            draw.ellipse((mx-mw, my-mh, mx+mw, my+mh), fill=(0,0,0))

        # 12. Nose
        nose_y = head_y + 40*ss
        nose_pts = get_pill_polygon(head_x, nose_y, 40*ss, 110*ss, 20*ss)
        nose_pts = [rotate_point(p, pivot, tilt) for p in nose_pts]
        draw.polygon(nose_pts, fill=spec.nose_color or (0,0,0))

        img = img.resize((self.w, self.h), Image.Resampling.LANCZOS)
        return img

def generate_fallback_video(character="male1", duration=2.5, fps=30, output="ugc/data/avatar_studio.mp4", speech=False, speech_text=None):
    # Automatic duration based on speech-text
    if speech_text:
        # Estimate duration: average speaking speed is 3 words per second
        word_count = len(speech_text.split())
        duration = max(2.0, word_count / 2.5 + 1.0)
        speech = True
        print(f"Speech detected. Calculated duration: {duration:.2f}s")

    studio = GeometricStudio()
    spec = PRESETS.get(character, PRESETS["male1"])
    total_frames = int(duration * fps)
    
    frames = []
    print(f"Rendering {character}...")
    for i in range(total_frames):
        t = i / fps
        energy = 0.0
        if speech:
            if speech_text:
                # Simulate speech envelope with word-breaks
                # We use a noisy low-freq oscillator modulated by word density
                energy = 0.4 + 0.5 * math.sin(t * 15) * math.cos(t * 7)
                energy = max(0, energy + 0.2 * np.random.normal())
                # Fade out energy at the very end
                if t > (duration - 0.5): energy *= (duration - t) * 2
            else:
                # Generic speech loop
                energy = 0.5 + 0.5 * math.sin(t * 12) * math.cos(t * 5)
                if (t % 1.5) > 1.2: energy = 0
            
        frame = studio.render_frame(t, spec, energy)
        frames.append(np.asarray(frame.convert("RGB")))
        if i % 10 == 0: print(f"Frame {i}/{total_frames}...")
            
    # Save MP4 using ffmpeg via subprocess for playable h264
    height, width, layers = frames[0].shape
    command = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        output
    ]
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    for frame in frames:
        process.stdin.write(frame.tobytes())
    process.stdin.close()
    process.wait()

    # Save GIF using ffmpeg (vastly faster than Pillow for high-res frames)
    gif_path = Path(output).with_suffix(".gif")
    gif_command = [
        'ffmpeg', '-y',
        '-i', output,
        '-vf', 'split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
        '-loop', '0',
        str(gif_path)
    ]
    subprocess.run(gif_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Done! Saved to {output} and {gif_path}")
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", default="male1", choices=list(PRESETS.keys()))
    parser.add_argument("--duration", type=float, default=2.5)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--output", default="ugc/data/avatar_studio.mp4")
    parser.add_argument("--speech", action="store_true")
    parser.add_argument("--speech-text", type=str, help="Text for the avatar to 'speak'")
    args = parser.parse_args()

    generate_fallback_video(
        character=args.character,
        duration=args.duration,
        fps=args.fps,
        output=args.output,
        speech=args.speech,
        speech_text=args.speech_text
    )

if __name__ == "__main__":
    main()
