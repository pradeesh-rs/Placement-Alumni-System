import ollama

def calculate_cgpa(marksheet_file):
    try:
        image_bytes = marksheet_file.read()
        
        response = ollama.chat(
            model='gemini-3-flash-preview:latest',
            messages=[{
                'role': 'user',
                'content': "Extract the final Cumulative GPA (CGPA) from this image. Only return the number.",
                'images': [image_bytes]
            }],
            options={
                'thinking_level': 'medium' # Specific to Gemini 3 series
            }
        )
        
        raw_text = response['message']['content'].strip()
        cgpa_val = "".join(c for c in raw_text if c.isdigit() or c == '.')
        return float(cgpa_val) if cgpa_val else 0.0

    except Exception as e:
        print(f"Gemini 3 Flash Error: {e}")
        return 0.0