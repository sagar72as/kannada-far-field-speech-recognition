# Far-Field Kannada Speech Recognition via Beamforming Enhancement
### Major Project Phase-1 Demonstration & Research Portal
**Institution:** Nitte Meenakshi Institute of Technology, Bengaluru  
**Department:** Electronics and Communication Engineering  

---

## 📌 Project Overview
This project addresses the severe degradation of distant speech in regional languages. Far-field speech captured in real environments (classrooms, smart rooms, public kiosks) is corrupted by noise, reverberation, and room acoustics.

By employing a front-end **4-microphone Uniform Linear Array (ULA)** with **Delay-and-Sum (DS) beamforming** and **5th-order Butterworth bandpass filtering (80 Hz – 7500 Hz)**, the signal achieves a **$\approx 6\text{ dB}$ spatial SNR improvement**. When fed into **OpenAI Whisper Medium** configured with forced regional decoding (`language="kn"`), the transcription transitions from garbled hallucinations to coherent, phonetically accurate Kannada text.

---

## 🚀 Web Application Features
The web application is an interactive simulation and project showcase:

1. **Interactive Audio DSP Lab:**
   - Pre-loaded authentic Kannada speech samples or custom `.wav`/`.mp3` audio upload.
   - Real-time parameter controls for **AWGN SNR** ($-5\text{ dB}$ to $+25\text{ dB}$), **Direction of Arrival** ($\theta = -60^\circ$ to $+60^\circ$), and filter toggles.
   - **A/B/C Audition Deck:** Listen directly to Clean Reference, Raw Far-Field Noisy Mic, and Beamformed Output in real-time using Web Audio API synthesis and spatial filtering.
2. **Interactive Visualizers:**
   - **Dual Oscilloscope Waveform:** Real-time time-domain comparison between raw noisy signal and enhanced signal.
   - **Frequency Spectral Density:** Live FFT frequency analysis showing noise floor cancellation and bandpass attenuation.
   - **ULA Array Beampattern:** Interactive polar response showing main lobe directivity and null steering at broadside.
3. **ASR Inference Results & Metrics:**
   - Side-by-side Whisper transcription comparison highlighting failure tokens vs. clean Kannada script.
   - Live Word Error Rate (WER) and Character Error Rate (CER) dynamics.
   - Phase-1 parameter comparison table directly from the project synopsis report.
4. **Interactive Architecture Stepper:**
   - 7-step pipeline walkthrough from audio acquisition to comparative evaluation.
5. **Codebase Viewer:**
   - Tabbed Python implementations for Delay-and-Sum beamforming, Butterworth filtering, and Whisper inference with one-click copy.
6. **Phase-2 Roadmap:**
   - Future plans for MVDR adaptive beamforming, Weighted Prediction Error (WPE) dereverberation, and physical microphone array deployment.

---

## 💻 Running the Webpage Locally

### Quick Start
To view the webpage, open a terminal in this directory and start any local HTTP server:

```bash
# Using Python
python -m http.server 8080
```

Then visit in your web browser:
```
http://localhost:8080/index.html
```

Or open `index.html` directly in any modern browser (Google Chrome, Microsoft Edge, Firefox, Brave).

---

## 📁 File Structure
```text
Automatic Speech Recognition/
├── index.html          # Semantic HTML5 web application structure
├── styles.css          # Modern dark-mode glassmorphism design system
├── app.js              # Real-time Web Audio DSP & canvas visualizers
├── majorproject.pdf    # Full Project Synopsis Document (NMIT ECE)
└── README.md           # Documentation & instructions
```
