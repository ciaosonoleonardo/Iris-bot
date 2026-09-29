def ask_openrouter_developer(prompt):
    if not OPENROUTER_API_KEY:
        return "Errore: OPENROUTER_API_KEY non trovata nelle variabili d'ambiente."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://gorhub.dev",
        "X-Title": "Gor Hub David Dev"
    }
    
    system_instruction = (
        "Sei David, il Lead Developer di Gor Hub. "
        "Rispondi sempre in italiano, in modo sintetico, preciso e altamente tecnico."
    )
    
    # Modelli gratuiti per account senza crediti registrati
    models_to_try = [
        "google/gemma-2-9b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "qwen/qwen-2-7b-instruct:free"
    ]
    
    for model_id in models_to_try:
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
            data = res.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
        except Exception:
            continue

    return "Errore: Tutti i modelli gratuiti sono momentaneamente occupati su OpenRouter. Riprova tra poco."
