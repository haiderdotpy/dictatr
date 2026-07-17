import requests

def speechtotext(audio):
    '''Returns the speech to text transcription of the given audio file in JSON format.'''
    response = requests.post(
        "http://127.0.0.1:8080/inference",
        files={"file": ("audio.wav", audio, "audio/wav")},
        data={
            "temperature": "0",
            "response_format": "json",
        },
    )

    print(f"STT Time: {response.elapsed.total_seconds():.2f}s")

    return (response.json()["text"] if response.status_code == 200 else None)