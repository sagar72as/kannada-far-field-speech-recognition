"""
Far-Field Kannada Speech Recognition Server
Provides static asset serving and robust real-time Speech-to-Text conversion for Kannada (kn-IN)
Supports audio of any duration with automatic chunking and noise-tolerant transcription.
"""

import http.server
import socketserver
import json
import io
import os
import sys
import wave

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def transcribe_kannada_audio(recognizer, audio_data):
    """
    Robust transcription for Kannada audio of any length.
    Handles short phrases as well as multi-sentence audio by chunking if needed.
    """
    raw_data = audio_data.get_raw_data()
    sample_rate = audio_data.sample_rate
    sample_width = audio_data.sample_width
    bytes_per_sec = sample_rate * sample_width
    total_duration = len(raw_data) / bytes_per_sec

    print(f"[ASR] Received audio: duration={total_duration:.2f}s, sample_rate={sample_rate}Hz")
    sys.stdout.flush()

    # If audio is up to 65 seconds, try full single-pass recognition first
    if total_duration <= 65.0:
        try:
            text = recognizer.recognize_google(audio_data, language="kn-IN")
            if text and text.strip():
                print(f"[ASR] Single-pass recognition succeeded ({total_duration:.2f}s): {text.strip()}")
                sys.stdout.flush()
                return text.strip(), total_duration
        except sr.UnknownValueError:
            print("[ASR] Single-pass returned UnknownValueError, attempting chunked analysis...")
        except Exception as e:
            print(f"[ASR] Single-pass error: {e}, attempting chunked analysis...")

    # Segment audio into 15-second windows with 1.5-second overlap
    chunk_sec = 15.0
    overlap_sec = 1.5
    chunk_bytes = int(chunk_sec * bytes_per_sec)
    step_bytes = int((chunk_sec - overlap_sec) * bytes_per_sec)
    total_bytes = len(raw_data)

    transcripts = []
    offset = 0
    chunk_idx = 1

    while offset < total_bytes:
        chunk_raw = raw_data[offset : offset + chunk_bytes]
        # Only process chunks with at least 1 second of audio
        if len(chunk_raw) >= int(1.0 * bytes_per_sec):
            chunk_audio = sr.AudioData(chunk_raw, sample_rate, sample_width)
            try:
                chunk_text = recognizer.recognize_google(chunk_audio, language="kn-IN")
                if chunk_text and chunk_text.strip():
                    cleaned = chunk_text.strip()
                    # Prevent identical contiguous duplicate phrases from overlap
                    if not transcripts or cleaned != transcripts[-1]:
                        transcripts.append(cleaned)
                    print(f"[ASR] Chunk {chunk_idx} ({offset/bytes_per_sec:.1f}s): {cleaned}")
            except sr.UnknownValueError:
                print(f"[ASR] Chunk {chunk_idx} ({offset/bytes_per_sec:.1f}s): (no speech recognized)")
            except Exception as e:
                print(f"[ASR] Chunk {chunk_idx} error: {e}")
        offset += step_bytes
        chunk_idx += 1

    if transcripts:
        combined_text = " ".join(transcripts)
        print(f"[ASR] Chunked recognition succeeded: {combined_text}")
        sys.stdout.flush()
        return combined_text, total_duration

    raise sr.UnknownValueError("No intelligible Kannada speech detected in the audio.")

class ASRRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        elif self.path == '/api/status':
            self.send_json({
                "status": "running",
                "asr_engine": "Google/Whisper Kannada kn-IN",
                "speech_recognition_available": HAS_SR
            })
            return
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/transcribe'):
            self.handle_transcribe()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_transcribe(self):
        if not HAS_SR:
            self.send_json({
                "success": False,
                "error": "dependency_missing",
                "message": "speech_recognition library is not installed."
            }, status=500)
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json({
                    "success": False,
                    "error": "empty_payload",
                    "message": "No audio payload received."
                }, status=400)
                return

            audio_bytes = self.rfile.read(content_length)

            # Recognize audio using SpeechRecognition
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 150
            recognizer.dynamic_energy_threshold = True

            wav_io = io.BytesIO(audio_bytes)

            try:
                with sr.AudioFile(wav_io) as source:
                    audio_data = recognizer.record(source)

                kannada_text, duration = transcribe_kannada_audio(recognizer, audio_data)

                self.send_json({
                    "success": True,
                    "text": kannada_text,
                    "language": "kn-IN",
                    "duration": round(duration, 2),
                    "status": "Transcribed successfully"
                })
            except sr.UnknownValueError:
                self.send_json({
                    "success": False,
                    "error": "unknown_value",
                    "message": "ಯಾವುದೇ ಸ್ಪಷ್ಟ ಧ್ವನಿ ಪತ್ತೆಯಾಗಿಲ್ಲ (No intelligible Kannada speech detected. Please speak clearly into the microphone or upload an audio file with clear speech.)"
                })
            except sr.RequestError as req_err:
                self.send_json({
                    "success": False,
                    "error": "request_error",
                    "message": f"ASR network service error: {str(req_err)}"
                })
            except Exception as e:
                self.send_json({
                    "success": False,
                    "error": "audio_parse_error",
                    "message": f"Could not parse audio format: {str(e)}"
                })

        except Exception as ex:
            self.send_json({
                "success": False,
                "error": "server_error",
                "message": str(ex)
            }, status=500)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ASRRequestHandler) as httpd:
        print(f"ASR Server running at http://localhost:{PORT}")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    run()
