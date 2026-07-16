import ollama 

def cleanup_transcript(transcript):
    '''Cleans up audio transcripts and returns output.'''
    response = ollama.chat(
        model="qwen3:0.6b",
        messages=[{
            'role': 'user', 
            'content': f'''
                Clean the following speech transcript.

                Rules:
                - Remove special characters and emojis which don't contribute to the meaning of the transcript.
                - Remove filler words (um, uh, you know, like) when they do not change meaning.
                - Restore punctuation and capitalization.
                - Preserve wording and intent.
                - Do not remove any content that changes the meaning of the transcript.
                - Do not summarize, rewrite, or omit information.
                - Output plain text only.

                Transcript:
                [transcript]{transcript}[/transcript]
            '''
        }],
        think=False,
        keep_alive=-1
    )

    return response['message']['content']