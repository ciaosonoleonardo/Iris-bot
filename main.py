def ask_groq_developer(prompt):
    if not GROQ_API_KEY:
        return "Errore: GROQ_API_KEY non trovata nelle variabili d'ambiente di Render."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    system_instruction = (
        "Sei David, il Lead Developer di Gor Hub. "
        "Rispondi sempre in italiano, in modo sintetico, preciso e tecnico."
    )
    payload = {
        "model": "llama-3.1-8b-instant",  # Se vuoi Llama 3.3 70B, usa "llama-3.3-70b-versatile"
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        res = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        data = res.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            print(f"DEBUG GROQ ERROR: {data['error']}")
            return f"Errore API Groq: {data['error'].get('message', 'Errore sconosciuto')}"
        else:
            return "Risposta non valida da Groq."
    except Exception as e:
        return f"Errore di connessione: {e}"
