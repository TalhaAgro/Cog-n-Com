import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv() # Load API_KEY from .env

client = genai.Client(api_key=os.environ.get("API_KEY"))

@csrf_exempt # Allow POST requests without CSRF token for the hackathon
def identify_song(request):
    if request.method == 'POST':
        try:
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return JsonResponse({'error': 'No audio provided'}, status=400)

            # Read the file into memory
            audio_bytes = audio_file.read()

            # Define the structure we want back
            schema = {
                "type": types.Type.OBJECT,
                "properties": {
                    "title": {"type": types.Type.STRING},
                    "artist": {"type": types.Type.STRING},
                    "album": {"type": types.Type.STRING},
                    "year": {"type": types.Type.STRING},
                    "genre": {"type": types.Type.STRING},
                    "mood": {"type": types.Type.STRING},
                },
                "required": ["title", "artist", "genre"],
            }

            # Call Gemini
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm"),
                    "Identify this song. Return JSON."
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema
                )
            )

            return JsonResponse(json.loads(response.text))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)