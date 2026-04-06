import flet as ft
import requests
import os
import json
import time

# --- CONFIGURATION API ---
GEMINI_API_KEY = "AIzaSyBpBTborM4zPEUHeCG4buAggAS_cI3jc3E"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# --- DESIGN TOKENS ---
COLOR_BG = "#050A10"
COLOR_PRIMARY = "#00FFFF"
COLOR_SECONDARY = "#1A2533"
COLOR_TEXT = "#E0F7FA"

# --- RESPONSES HORS-LIGNE ---
OFFLINE_RESPONSES = {
    "hello": "Système PocketAI en ligne. Mode local activé.",
    "aide": "Commandes : status, aide, clear.",
    "status": "État : Opérationnel. Réseau : Déconnecté.",
    "default": "Connexion internet requise pour l'IA complète. Mode tactique local actif."
}

class Message(ft.Column):
    def __init__(self, user_name, text, is_user):
        super().__init__()
        self.user_name = user_name
        self.text = text
        self.is_user = is_user
        
        self.controls = [
            ft.Text(self.user_name, size=12, weight="bold", color=COLOR_PRIMARY if is_user else "#FF00FF"),
            ft.Container(
                content=ft.Text(self.text, color=COLOR_TEXT),
                bgcolor=COLOR_SECONDARY if not is_user else "#001A33",
                padding=10,
                border_radius=10,
                border=ft.border.all(1, COLOR_PRIMARY if is_user else "#FF00FF")
            )
        ]
        self.horizontal_alignment = ft.CrossAxisAlignment.END if is_user else ft.CrossAxisAlignment.START

def main(page: ft.Page):
    try:
        page.title = "PocketAI Tactical"
        page.bgcolor = COLOR_BG
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 10
        
        # --- ETAT DE L'APPLICATION ---
        chat_history = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        
        memory = []
        try:
            history_raw = page.client_storage.get("chat_history")
            if history_raw:
                memory = json.loads(history_raw)
        except:
            pass

        # --- ÉLÉMENT VISUEL SANS ICÔNE (Zéro risque de crash) ---
        # Utilisation de ft.Alignment(0,0) au lieu de ft.alignment.center pour compatibilité
        orb = ft.Container(
            content=ft.Text("AI", color=COLOR_BG, weight="bold"),
            bgcolor=COLOR_PRIMARY,
            width=50, height=50,
            border_radius=25,
            alignment=ft.Alignment(x=0, y=0)
        )

        # Affichage de l'historique
        for msg in memory:
            try:
                role = "USER" if msg['role'] == 'user' else "IA"
                chat_history.controls.append(Message(role, msg['parts'][0]['text'], msg['role'] == 'user'))
            except:
                pass

        def call_ai(prompt, history):
            payload = {
                "contents": history + [{"role": "user", "parts": [{"text": prompt}]}],
                "system_instruction": {"parts": [{"text": "Tu es une IA tactique. Réponds brièvement."}]}
            }
            try:
                response = requests.post(API_URL, json=payload, timeout=8)
                if response.status_code == 200:
                    result = response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
            except:
                pass
            
            low_prompt = prompt.lower()
            return OFFLINE_RESPONSES.get(low_prompt, OFFLINE_RESPONSES["default"])

        def on_send_click(e):
            if not chat_field.value: return
            
            user_text = chat_field.value
            chat_field.value = ""
            chat_history.controls.append(Message("USER", user_text, True))
            page.update()
            
            bot_text = call_ai(user_text, memory)
            
            memory.append({"role": "user", "parts": [{"text": user_text}]})
            memory.append({"role": "model", "parts": [{"text": bot_text}]})
            
            try:
                truncated_memory = memory[-10:]
                page.client_storage.set("chat_history", json.dumps(truncated_memory))
            except:
                pass
            
            chat_history.controls.append(Message("IA", bot_text, False))
            page.update()

        chat_field = ft.TextField(
            hint_text="Commande...",
            expand=True, border_color=COLOR_PRIMARY,
            on_submit=on_send_click,
            bgcolor=COLOR_SECONDARY
        )

        # Bouton d'envoi
        send_btn = ft.ElevatedButton(
            text="SEND",
            on_click=on_send_click,
            bgcolor=COLOR_PRIMARY,
            color=COLOR_BG
        )

        # Assemblage final - Alignment centre simplifié
        page.add(
            ft.Row([ft.Text("POCKET AI", size=20, weight="bold", color=COLOR_PRIMARY)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(content=orb, alignment=ft.Alignment(0, 0), padding=5),
            ft.Container(content=chat_history, expand=True, border=ft.border.all(1, "#111B27"), padding=10, border_radius=10),
            ft.Row([chat_field, send_btn])
        )

    except Exception as e:
        # ÉCRAN DE DIAGNOSTIC ROUGE (Si tout le reste échoue)
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("ERREUR CRITIQUE", color="red", size=20, weight="bold"),
                ft.Text(f"Détails : {str(e)}", color="white"),
                ft.Text("Veuillez réinitialiser l'application.", color="gray")
            ]),
            bgcolor="black", expand=True, padding=20
        ))

ft.app(target=main)
