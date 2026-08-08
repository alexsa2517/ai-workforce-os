"""
Video Assembly Service - Combines clips, audio, and effects into final video.
Uses ffmpeg for professional-grade video assembly.
"""
import logging
import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ai_workforce.video.assembly")


class VideoAssemblyService:
    """
    Assembles video clips into final output with audio mixing.

    Features:
    - Concatenate video clips with transitions
    - Mix narration + BGM + sound effects
    - Normalize audio levels
    - Add subtitles (optional)
    """

    def __init__(self, output_dir: str = "./movies"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check ffmpeg availability
        self._ffmpeg_available = self._check_ffmpeg()
        if not self._ffmpeg_available:
            logger.warning("ffmpeg not found. Video assembly will not work.")

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is installed."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    async def assemble(
        self,
        clips: List[Dict[str, Any]],
        output_filename: str,
        bgm_path: Optional[str] = None,
        narration_segments: Optional[List[Dict[str, Any]]] = None,
        transition_type: str = "fade",
        transition_duration: float = 0.5,
    ) -> str:
        """
        Assemble video from clips.

        Args:
            clips: List of {path, duration, start_time}
            output_filename: Output filename
            bgm_path: Background music file path
            narration_segments: List of {path, start_time, duration}
            transition_type: Type of transition between clips
            transition_duration: Transition duration in seconds

        Returns:
            Path to assembled video file
        """
        if not self._ffmpeg_available:
            raise RuntimeError("ffmpeg is not available. Cannot assemble video.")

        if not clips:
            raise ValueError("No clips provided for assembly")

        output_path = self.output_dir / output_filename

        try:
            # Step 1: Create concat list file
            concat_list = self._create_concat_list(clips, transition_type, transition_duration)

            # Step 2: Concatenate video clips
            temp_video = self.output_dir / f"temp_{output_filename}"
            await self._concatenate_clips(concat_list, str(temp_video))

            # Step 3: Mix audio (if provided)
            if bgm_path or narration_segments:
                await self._mix_audio(
                    video_path=str(temp_video),
                    output_path=str(output_path),
                    bgm_path=bgm_path,
                    narration_segments=narration_segments,
                )
            else:
                # Just rename temp to final
                os.rename(str(temp_video), str(output_path))

            logger.info(f"Video assembly complete: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            raise

    def _create_concat_list(
        self,
        clips: List[Dict[str, Any]],
        transition_type: str,
        transition_duration: float,
    ) -> str:
        """Create ffmpeg concat demuxer list file."""
        concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)

        for i, clip in enumerate(clips):
            clip_path = clip["path"]
            if not os.path.exists(clip_path):
                logger.warning(f"Clip not found: {clip_path}")
                continue

            # Write file entry
            concat_file.write(f"file '{os.path.abspath(clip_path)}'\n")

            # Add duration hint
            duration = clip.get("duration", 5.0)
            concat_file.write(f"duration {duration}\n")

        concat_file.close()
        return concat_file.name

    async def _concatenate_clips(self, concat_list: str, output_path: str) -> None:
        """Concatenate clips using ffmpeg concat demuxer."""
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            "-movflags", "+faststart",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"ffmpeg concat error: {result.stderr}")
            raise RuntimeError(f"Failed to concatenate clips: {result.stderr[:500]}")

        # Clean up concat list
        os.unlink(concat_list)
        logger.info(f"Clips concatenated to: {output_path}")

    async def _mix_audio(
        self,
        video_path: str,
        output_path: str,
        bgm_path: Optional[str],
        narration_segments: Optional[List[Dict[str, Any]]],
    ) -> None:
        """Mix video audio with BGM and narration."""
        # Build complex filter for audio mixing
        filter_complex = []
        inputs = ["-i", video_path]

        input_idx = 1
        audio_streams = []

        # Add BGM
        if bgm_path and os.path.exists(bgm_path):
            inputs.extend(["-i", bgm_path])
            # Loop BGM to match video duration, reduce volume
            filter_complex.append(
                f"[{input_idx}:a]aloop=loop=-1:size=2e+09,afade=t=out:st=0:d=2,volume=0.3[bgm]"
            )
            audio_streams.append("[bgm]")
            input_idx += 1

        # Add narration segments
        if narration_segments:
            for seg in narration_segments:
                seg_path = seg.get("path")
                if seg_path and os.path.exists(seg_path):
                    inputs.extend(["-i", seg_path])
                    start_time = seg.get("start_time", 0)
                    # Delay narration to start at correct time
                    filter_complex.append(
                        f"[{input_idx}:a]adelay={int(start_time * 1000)}|{int(start_time * 1000)},volume=1.0[narr_{input_idx}]"
                    )
                    audio_streams.append(f"[narr_{input_idx}]")
                    input_idx += 1

        if not audio_streams:
            # No additional audio, just copy
            cmd = ["ffmpeg", "-y", "-i", video_path, "-c", "copy", output_path]
        else:
            # Mix all audio streams
            mix_inputs = "".join(audio_streams)
            filter_complex.append(
                f"{mix_inputs}amix=inputs={len(audio_streams)}:duration=longest:normalize=0[outa]"
            )

            cmd = [
                "ffmpeg", "-y",
                *inputs,
                "-filter_complex", ";".join(filter_complex),
                "-map", "0:v",  # Video from first input
                "-map", "[outa]",  # Mixed audio
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                output_path,
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"ffmpeg audio mix error: {result.stderr}")
            raise RuntimeError(f"Failed to mix audio: {result.stderr[:500]}")

        logger.info(f"Audio mixed successfully: {output_path}")

    async def extract_final_frame(self, video_path: str, output_path: str) -> str:
        """Extract the final frame from a video for keyframe reuse."""
        if not self._ffmpeg_available:
            raise RuntimeError("ffmpeg not available")

        cmd = [
            "ffmpeg",
            "-y",
            "-sseof", "-1",  # Seek to 1 second before end
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"ffmpeg frame extraction error: {result.stderr}")
            raise RuntimeError(f"Failed to extract frame: {result.stderr[:500]}")

        return output_path

    async def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video metadata using ffprobe."""
        if not self._ffmpeg_available:
            return {}

        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "json",
            video_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {}

        import json
        try:
            data = json.loads(result.stdout)
            return {
                "duration": float(data.get("format", {}).get("duration", 0)),
                "width": data.get("streams", [{}])[0].get("width"),
                "height": data.get("streams", [{}])[0].get("height"),
                "fps": data.get("streams", [{}])[0].get("r_frame_rate"),
            }
        except (json.JSONDecodeError, ValueError):
            return {}
