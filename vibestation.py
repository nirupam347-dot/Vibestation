import math
import random
import sys
import time
import numpy as np
import pygame
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()

# --- AUDIO GENERATION (Procedural Lo-Fi Chords & Soft Noise) ---
SAMPLE_RATE = 44100

def generate_ambient_buffer(duration=6.0):
    """Generates a soft, warm ambient chord progression in stereo."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Base frequencies: D minor 9 chord (D3, F3, A3, C4, E4)
    frequencies = [146.83, 174.61, 220.00, 261.63, 329.63]
    signal = np.zeros_like(t)

    # Layer warm sine waves with slow tremolo/beating
    for i, freq in enumerate(frequencies):
        detune = 1.0 + (i * 0.0015)
        vibrato = np.sin(2 * np.pi * 0.25 * t + i) * 1.5
        layer = np.sin(2 * np.pi * (freq * detune + vibrato) * t)
        
        # Soft envelope (fade in / fade out)
        envelope = np.sin(np.pi * t / duration) ** 2
        signal += layer * envelope * 0.45

    # Add gentle low-passed background vinyl/pink noise
    noise = np.random.normal(0, 0.015, len(t))
    signal = signal + noise

    # Clip to prevent distortion and convert to 16-bit PCM stereo
    signal = np.clip(signal, -0.9, 0.9)
    stereo_signal = np.ascontiguousarray(np.vstack((signal, signal)).T)
    return (stereo_signal * 32767).astype(np.int16)

def start_audio():
    """Initializes pygame mixer and plays ambient drone loop."""
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=2048)
    raw_buffer = generate_ambient_buffer(duration=8.0)
    sound = pygame.sndarray.make_sound(raw_buffer)
    # Loop infinitely
    sound.play(loops=-1)

# --- VISUALS & TERMINAL UI ---
VIBE_QUOTES = [
    "stay in flow state",
    "pure aesthetic, zero friction",
    "crafting pixels & logic",
    "breathe in, deploy out",
    "quiet mind, clean code",
]

def make_wave_visualizer(step: int, width: int = 40) -> str:
    """Generates an animated audio wave visualizer."""
    chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    bars = []
    for i in range(width):
        # Layered sine waves for organic fluid movement
        val = (math.sin(i * 0.3 + step * 0.2) + 1) * 0.5
        val += (math.cos(i * 0.15 - step * 0.1) + 1) * 0.25
        val = min(1.0, val / 1.5)
        idx = int(val * (len(chars) - 1))
        bars.append(chars[idx])
    return "".join(bars)

def create_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", size=8),
        Layout(name="footer", size=3),
    )
    return layout

def main():
    try:
        start_audio()
    except Exception as e:
        console.print(f"[dim yellow]Audio unavailable ({e}). Continuing in silent visualizer mode...[/dim yellow]")

    layout = create_layout()
    step = 0
    quote_index = 0
    start_time = time.time()

    with Live(layout, refresh_per_second=15, screen=True):
        while True:
            step += 1
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)

            # Change quote every 10 seconds
            if step % 150 == 0:
                quote_index = (quote_index + 1) % len(VIBE_QUOTES)

            # Header
            header_text = Text("✦ V I B E   S T A T I O N ✦", style="bold magenta", justify="center")
            layout["header"].update(Panel(header_text, border_style="dim magenta"))

            # Body: Waveform & Quote
            bars = make_wave_visualizer(step, width=48)
            body_content = Text()
            body_content.append(f"\n{bars}\n\n", style="cyan")
            body_content.append(f"“{VIBE_QUOTES[quote_index]}”", style="italic bright_white")
            layout["body"].update(Panel(Align.center(body_content), border_style="dim cyan"))

            # Footer: Timer & Status
            status_text = Text(f"Mode: Focused Deep Work  •  Session: {mins:02d}:{secs:02d}  •  Ctrl+C to Exit", style="dim white")
            layout["footer"].update(Panel(Align.center(status_text), border_style="dim white"))

            time.sleep(0.06)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.mixer.quit()
        console.print("\n[dim magenta]Session ended. Stay creative.[/dim magenta]\n")
        sys.exit(0)