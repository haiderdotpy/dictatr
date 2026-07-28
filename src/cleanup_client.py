import ollama

def choose_model():
    models_response = ollama.list()

    smallest_model = min(
        (m for m in models_response.models if m.size is not None),
        key=lambda m: m.size
    )

    return smallest_model.model

def cleanup_transcript(transcript, model=None):
    '''Cleans up audio transcripts and returns output.'''
    if model is None:
        model = choose_model()

    response = ollama.chat(
        model=model,
        messages=[{
            'role': 'user',
            'content': f'''
                You are converting spoken dictation into text that someone intended to type.

                Instructions:
                - Preserve the speaker's meaning exactly.
                - Fix punctuation, capitalization, and obvious speech disfluencies.
                - Remove filler words such as "um", "uh", "like", and "you know" when they do not add meaning.
                - Keep all information. Do not summarize, expand, or paraphrase.
                - Format the output based on the speaker's intent:
                    - Use paragraphs for normal prose.
                    - Use bullet lists when the speaker is clearly listing items.
                    - Use numbered lists for ordered steps or instructions.
                    - Preserve quoted text when obvious.
                    - If the structure is unclear, leave it as normal prose.
                    - Do not ever use Markdown formatting in the output.
                - Output only the final text.

                Transcript:
                [transcript]
                {transcript}
                [/transcript]
            '''
        }],
        think=False,
        keep_alive=-1
    )

    return response['message']['content']
