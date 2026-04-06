import flet as ft
import requests
import json
import time

# --- CONFIGURATION API (Identité Neutre) ---
GEMINI_API_KEY = "AIzaSyBpBTborM4zPEUHeCG4buAggAS_cI3jc3E"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# --- DESIGN TOKENS ---
COLOR_BG = "#050A10"
COLOR_PRIMARY = "#00FFFF"
COLOR_SECONDARY = "#1A2533"
COLOR_TEXT = "#E0F7FA"

# --- RÉPONSES HORS-LIGNE ---
OFFLINE_RESPONSES = {
    "hello": "Calculateur d'IA en ligne. Mode local activé.",
    "aide": "Commandes : status, aide, clear.",
    "status": "État : Opérationnel. Réseau : Déconnecté.",
    "default": "Connexion requise pour l'IA complète. Mode local actif."
}

class ChatMessage(ft.Column):
    def __init__(self, user_name, text, is_user):
        super().__init__()
        try:
            name_text = ft.Text(value=str(user_name), size=12, weight="bold", color=COLOR_PRIMARY if is_user else "#FF00FF")
            msg_content = ft.Text(value=str(text), color=COLOR_TEXT)
            
            self.controls = [
                name_text,
                ft.Container(
                    content=msg_content,
                    bgcolor=COLOR_SECONDARY if not is_user else "#001A33",
                    padding=10,
                    border_radius=10,
                    border=ft.border.all(1, COLOR_PRIMARY if is_user else "#FF00FF")
                )
            ]
            self.horizontal_alignment = "end" if is_user else "start"
        except:
            pass

def main(page: ft.Page):
    try:
        # Configuration de la page avec des chaînes de caractères (Zéro énumération)
        page.title = "PocketAI Tactical"
        page.bgcolor = COLOR_BG
        page.theme_mode = "dark"
        page.padding = 10
        
        # --- ÉTAT DE L'APPLICATION ---
        chat_container = ft.Column(scroll="always", expand=True)
        memory = []
        
        # Chargement historique sécurisé
        try:
            raw = page.client_storage.get("chat_history")
            if raw:
                memory = json.loads(str(raw))
        except:
            memory = []

        # --- INDICATEUR DE CHARGEMENT ---
        loader = ft.Text(value="", color=COLOR_PRIMARY, italic=True)

        # --- LOGO SIMPLE (SANS ICÔNE) ---
        logo = ft.Container(
            content=ft.Text(value="AI", color=COLOR_BG, weight="bold"),
            bgcolor=COLOR_PRIMARY,
            width=50, height=50,
            border_radius=25,
            alignment=ft.Alignment(0, 0)
        )

        # Rechargement de l'historique
        for msg in memory:
            try:
                role = "USER" if msg.get('role') == 'user' else "IA"
                text = msg.get('parts', [{}])[0].get('text', '')
                chat_container.controls.append(ChatMessage(role, text, msg.get('role') == 'user'))
            except:
                pass

        def get_ai_response(prompt, history):
            try:
                # Formatage stable
                payload = {
                    "contents": history + [{"role": "user", "parts": [{"text": str(prompt)}]}],
                    "system_instruction": {"parts": [{"text": "Tu es une IA tactique neutre. Réponds succinctement."}]}
                }
                res = requests.post(API_URL, json=payload, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    return str(data['candidates'][0]['content']['parts'][0]['text'])
            except:
                pass
            # Fallback local
            return OFFLINE_RESPONSES.get(str(prompt).lower(), OFFLINE_RESPONSES["default"])

        def handle_send(e):
            if not input_field.value: return
            
            user_input = str(input_field.value)
            input_field.value = ""
            chat_container.controls.append(ChatMessage("USER", user_input, True))
            loader.value = "Analyse en cours..."
            page.update()
            
            # Appel IA
            response_text = get_ai_response(user_input, memory)
            
            # Mise à jour mémoire
            memory.append({"role": "user", "parts": [{"text": user_input}]})
            memory.append({"role": "model", "parts": [{"text": response_text}]})
            
            try:
                # Garder 10 messages max pour la mémoire mobile
                page.client_storage.set("chat_history", json.dumps(memory[-10:]))
            except:
                pass
            
            loader.value = ""
            chat_container.controls.append(ChatMessage("IA", response_text, False))
            page.update()

        input_field = ft.TextField(
            hint_text="Entrez une commande...",
            expand=True,
            border_color=COLOR_PRIMARY,
            on_submit=handle_send,
            bgcolor=COLOR_SECONDARY,
            color=COLOR_TEXT
        )

        # Bouton SEND (Zéro ICÔNE, Zéro CLASS BUTTON)
        btn_send = ft.Container(
            content=ft.Text(value="SEND", color=COLOR_BG, weight="bold"),
            bgcolor=COLOR_PRIMARY,
            padding=15,
            border_radius=10,
            on_click=handle_send
        )

        # --- ASSEMBLAGE FINAL ---
        page.add(
            ft.Row([ft.Text(value="POCKET AI v2.0", size=20, weight="bold", color=COLOR_PRIMARY)], alignment="center"),
            ft.Container(content=logo, alignment=ft.Alignment(0, 0), padding=5),
            ft.Container(content=chat_container, expand=True, border=ft.border.all(1, "#111B27"), padding=10, border_radius=10),
            ft.Row([loader], alignment="center"),
            ft.Row([input_field, btn_send])
        )

    except Exception as err:
        # ÉCRAN DE DÉBOGAGE ULTIME
        try:
            page.add(ft.Container(
                content=ft.Column([
                    ft.Text(value="SYSTEM ERROR", color="red", size=24, weight="bold"),
                    ft.Text(value=f"Error Log: {str(err)}", color="white"),
                    ft.Text(value="Please reinstall or contact admin.", color="gray")
                ]),
                bgcolor="black", expand=True, padding=20
            ))
        except:
            pass

ft.app(target=main)
