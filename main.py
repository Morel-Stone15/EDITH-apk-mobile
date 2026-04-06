import flet as ft
import google.generativeai as genai
import os
import requests
import json
import time

# --- CONFIGURATION API ---
GEMINI_API_KEY = "AIzaSyBpBTborM4zPEUHeCG4buAggAS_cI3jc3E"
genai.configure(api_key=GEMINI_API_KEY)

# --- DESIGN TOKENS (E.D.I.T.H STYLE) ---
COLOR_BG = "#050A10"  # Noir Holographique
COLOR_PRIMARY = "#00FFFF"  # Cyan Néon
COLOR_SECONDARY = "#1A2533"  # Bleu Cobalt Profond
COLOR_TEXT = "#E0F7FA"  # Blanc Glacé

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
    page.title = "E.D.I.T.H Tactical Assistant"
    page.bgcolor = COLOR_BG
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 400
    page.window_height = 800
    
    # --- ETAT DE L'APPLICATION ---
    chat_history = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    
    # --- ANIMATION DE L'ORBE ---
    def create_orb():
        return ft.Container(
            width=100,
            height=100,
            shape=ft.BoxShape.CIRCLE,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=1,
                colors=[COLOR_PRIMARY, "transparent"],
            ),
            shadow=ft.BoxShadow(spread_radius=10, blur_radius=20, color=COLOR_PRIMARY),
            animate_opacity=300,
            opacity=0.5
        )

    orb = create_orb()
    
    # --- INITIALISATION GEMINI ---
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction="Tu es E.D.I.T.H, l'IA tactique de Tony Stark. Ton ton est professionnel, précis, un peu ironique mais loyal. Réponds brièvement."
    )
    
    # Restauration de la mémoire depuis le stockage local (Android/PWA)
    history_raw = page.client_storage.get("chat_history")
    history = json.loads(history_raw) if history_raw else []
    chat = model.start_chat(history=history)

    # Affichage de l'historique au démarrage
    for msg in history:
        is_user = msg['role'] == 'user'
        chat_history.controls.append(Message("HUMAIN" if is_user else "E.D.I.T.H", msg['parts'][0], is_user))

    def on_send_click(e):
        if not chat_field.value:
            return
        
        user_text = chat_field.value
        chat_field.value = ""
        
        # Ajout message utilisateur
        chat_history.controls.append(Message("HUMAIN", user_text, True))
        orb.opacity = 1.0 # L'orbe s'allume lors de la réflexion
        page.update()
        
        try:
            # Envoi à Gemini
            response = chat.send_message(user_text)
            bot_text = response.text
            
            # Ajout réponse IA
            chat_history.controls.append(Message("E.D.I.T.H", bot_text, False))
            
            # Sauvegarde mémoire (FIFO 20 messages)
            new_history = chat.history[-20:]
            history_serializable = [{"role": m.role, "parts": [m.parts[0].text]} for m in new_history]
            page.client_storage.set("chat_history", json.dumps(history_serializable))
            
        except Exception as err:
            chat_history.controls.append(Message("SYSTEM", f"Erreur de communication : {err}", False))
        
        orb.opacity = 0.5
        page.update()

    chat_field = ft.TextField(
        hint_text="Saisissez une commande tactique...",
        expand=True,
        border_color=COLOR_PRIMARY,
        focused_border_color=COLOR_PRIMARY,
        on_submit=on_send_click
    )

    # --- LAYOUT FINAL ---
    page.add(
        ft.Row([ft.Text("E.D.I.T.H", size=24, weight="bold", color=COLOR_PRIMARY)], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(color=COLOR_PRIMARY, thickness=0.5),
        ft.Container(
            content=orb,
            alignment=ft.alignment.center,
            margin=ft.margin.only(top=20, bottom=20)
        ),
        ft.Container(
            content=chat_history,
            expand=True,
            border=ft.border.all(0.5, COLOR_PRIMARY),
            padding=10,
            border_radius=5
        ),
        ft.Row([
            chat_field,
            ft.IconButton(ft.icons.SEND_ROUNDED, icon_color=COLOR_PRIMARY, on_click=on_send_click)
        ])
    )

ft.app(target=main)
