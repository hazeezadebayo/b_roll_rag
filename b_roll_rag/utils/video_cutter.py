"""
TLDR: Executable FFmpeg wrapper.
Logic: Leverages Python `subprocess` to trigger headless video encoding. Injects complex 
filtergraphs specifically for dynamic aspect ratio formatting (e.g., blurring standard 16:9 
video into a 9:16 portrait canvas). Also implements a complete local fallback generator.
"""
import subprocess
import os
import cv2
import numpy as np

class VideoCutter:
    @staticmethod
    def cut_video(input_path: str, start_time: float, end_time: float, output_path: str, aspect_ratio: str = "original") -> str:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
            
        duration = end_time - start_time
        target_res = {"9:16": "1080:1920", "16:9": "1920:1080", "1:1": "1080:1080"}.get(aspect_ratio)

        command = ["ffmpeg", "-y", "-ss", str(start_time), "-i", input_path, "-t", str(duration)]

        if target_res:
            filtergraph = (
                f"[0:v]split=2[bg][fg];"
                f"[bg]scale={target_res}:force_original_aspect_ratio=increase,crop={target_res},boxblur=20:20[bg_blurred];"
                f"[fg]scale={target_res}:force_original_aspect_ratio=decrease[fg_scaled];"
                f"[bg_blurred][fg_scaled]overlay=(W-w)/2:(H-h)/2[outv]"
            )
            command.extend(["-filter_complex", filtergraph, "-map", "[outv]", "-map", "0:a?"])
        
        command.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac", output_path])
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")

def generate_fallback_video(character: str, speech_text: str, output: str):
    """Fallback utility replacing external dependencies with a raw OpenCV generated video."""
    width, height, fps, duration = 640, 480, 24, 3
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output, fourcc, fps, (width, height))
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i in range(fps * duration):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(frame, speech_text[:len(speech_text)//2], (50, 200), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, speech_text[len(speech_text)//2:], (50, 250), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        out.write(frame)
    out.release()

if __name__ == "__main__":
    generate_fallback_video("bot", "This is a test fallback video.", "test_fallback.mp4")
    print("Fallback generated at test_fallback.mp4")