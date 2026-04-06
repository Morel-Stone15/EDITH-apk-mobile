import flet as ft
import requests
import os
import json
import time

# --- CONFIGURATION API ---
GEMINI_API_KEY = "AIzaSyBpBTborM4zPEUHeCG4buAggAS_cI3jc3E"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# --- DESIGN TOKENS ---
COLOR_BG = "#050A10"
COLOR_PRIMARY = "#00FFFF"
COLOR_SECONDARY = "#1A2533"
COLOR_TEXT = "#E0F7FA"

# --- RESPONSES HORS-LIGNE (FALLBACK) ---
OFFLINE_RESPONSES = {
    "hello": "Système en ligne. Mode local activé (Hors-ligne).",
    "aide": "Commandes locales : 'status', 'aide', 'clear'.",
    "status": "Diagnostic : Batterie OK, Stockage OK, Connexion : Déconnecté.",
    "default": "Mode Hors-ligne : Connexion internet requise pour une analyse avancée. Protocoles de base opérationnels."
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
                border_radius=ft.border_radius.only(
                    top_left=10, top_right=10, 
                    bottom_right=0 if is_user else 10,
                    bottom_left=10 if is_user else 0
                ),
                border=ft.border.all(1, COLOR_PRIMARY if is_user else "#FF00FF")
            )
        ]
        self.horizontal_alignment = ft.CrossAxisAlignment.END if is_user else ft.CrossAxisAlignment.START

def main(page: ft.Page):
    try:
        page.title = "PocketAI Tactical"
        page.bgcolor = COLOR_BG
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20
        
        # --- ETAT DE L'APPLICATION ---
        chat_history = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        
        # Récupération de l'historique sécurisée
        try:
            history_raw = page.client_storage.get("chat_history")
            memory = json.loads(history_raw) if history_raw else []
        except Exception:
            memory = []

        # --- ANIMATION DE L'ORBE ---
        orb = ft.Container(
            width=80, height=80, shape=ft.BoxShape.CIRCLE,
            gradient=ft.RadialGradient(colors=[COLOR_PRIMARY, "transparent"]),
            shadow=ft.BoxShadow(spread_radius=5, blur_radius=15, color=COLOR_PRIMARY),
            animate_opacity=300, opacity=0.5
        )

        # Affichage de l'historique
        for msg in memory:
            role = "USER" if msg['role'] == 'user' else "AI"
            chat_history.controls.append(Message(role, msg['parts'][0]['text'], msg['role'] == 'user'))

        def call_ai(prompt, history):
            # 1. Tentative avec Gemini (Online)
            payload = {
                "contents": history + [{"role": "user", "parts": [{"text": prompt}]}],
                "system_instruction": {"parts": [{"text": "Tu es une IA tactique professionnelle et précise. Ton ton est neutre et efficace. Réponds brièvement."}]}
            }
            try:
                response = requests.post(API_URL, json=payload, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
            except Exception:
                pass
            
            # 2. Fallback Hors-ligne (Offline)
            low_prompt = prompt.lower()
            return OFFLINE_RESPONSES.get(low_prompt, OFFLINE_RESPONSES["default"])

        def on_send_click(e):
            if not chat_field.value: return
            
            user_text = chat_field.value
            chat_field.value = ""
            chat_history.controls.append(Message("USER", user_text, True))
            orb.opacity = 1.0 
            page.update()
            
            bot_text = call_ai(user_text, memory)
            
            memory.append({"role": "user", "parts": [{"text": user_text}]})
            memory.append({"role": "model", "parts": [{"text": bot_text}]})
            
            truncated_memory = memory[-20:]
            page.client_storage.set("chat_history", json.dumps(truncated_memory))
            
            chat_history.controls.append(Message("AI", bot_text, False))
            orb.opacity = 0.5
            page.update()

        chat_field = ft.TextField(
            hint_text="Entrez une commande...",
            expand=True, border_color=COLOR_PRIMARY,
            on_submit=on_send_click
        )

        page.add(
            ft.Row([ft.Text("POCKET AI", size=24, weight="bold", color=COLOR_PRIMARY)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color="#111B27", thickness=1),
            ft.Container(content=orb, alignment=ft.alignment.center, padding=10),
            ft.Container(content=chat_history, expand=True, border=ft.border.all(0.5, "#111B27"), padding=10, border_radius=10),
            ft.Row([chat_field, ft.IconButton(ft.icons.SEND_ROUNDED, icon_color=COLOR_PRIMARY, on_click=on_send_click)])
        )

    except Exception as e:
        # ÉCRAN DE DIAGNOSTIC (S'affiche si l'app plante au démarrage)
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("ERREUR TACTIQUE AU LANCEMENT", color="red", size=20, weight="bold"),
                ft.Text(f"Détails : {str(e)}", color="white"),
                ft.Text("Vérifiez les dépendances et le stockage.", color="gray")
            ]),
            bgcolor="black", expand=True, padding=50
        ))

ft.app(target=main)
