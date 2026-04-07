import flet as ft
import requests
import json
import time

# --- CONFIGURATION API (Identité Neutre & Professionnelle) ---
GEMINI_API_KEY = "AIzaSyBpBTborM4zPEUHeCG4buAggAS_cI3jc3E"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# --- DESIGN SYSTEM "CYBER-TACTICAL" ---
COLOR_BG = "#020408"
# On utilise un bleu "Cyber" avec un léger mélange de vert pour un look plus "radar"
COLOR_PRIMARY = "#00D4FF" 
COLOR_ACCENT = "#FF00FF"
COLOR_GLASS = "#101620"
COLOR_TEXT_MAIN = "#E0F7FA"

# --- RÉPONSES HORS-LIGNE (SYSTÈME DE SECOURS) ---
OFFLINE_PROTOCOLS = {
    "status": "STATUT SYSTÈME : OPÉRATIONNEL. RÉSEAU EXTERNE : DÉCONNECTÉ. MODE LOCAL ACTIF.",
    "aide": "OPTIONS DISPONIBLES : [STATUS], [AIDE], [CLEAR], [MODE].",
    "ping": "PONG. LATENCE LOCALE : 0.02ms.",
    "hello": "UNITÉ TACTIQUE EN LIGNE. EN ATTENTE DE CONSIGNES.",
    "default": "CONNEXION INTERNET INDISPONIBLE. ANALYSE IA GÉNÉRATIVE SUSPENDUE. UTILISEZ LES COMMANDES LOCALES [AIDE]."
}

class TacticalMessage(ft.Column):
    def __init__(self, role, text, is_user):
        super().__init__()
        try:
            name_label = ft.Text(
                value=str(role).upper(), 
                size=10, 
                weight="bold", 
                color=COLOR_PRIMARY if is_user else COLOR_ACCENT,
                font_family="monospace" # Police type "code"
            )
            
            self.controls = [
                name_label,
                ft.Container(
                    content=ft.Text(value=str(text), color=COLOR_TEXT_MAIN, size=14),
                    bgcolor=COLOR_GLASS if not is_user else "#081E2F",
                    padding=12,
                    border_radius=ft.border_radius.only(
                        top_left=0 if not is_user else 15,
                        top_right=15 if not is_user else 0,
                        bottom_left=15,
                        bottom_right=15
                    ),
                    border=ft.border.all(1, "#1A3A4F" if is_user else "#3F1D4F"),
                    blur=ft.Blur(sigma_x=10, sigma_y=10) # Effet visuel "verre"
                )
            ]
            self.horizontal_alignment = "end" if is_user else "start"
        except:
            pass

def main(page: ft.Page):
    try:
        # Configuration UI "Technologique"
        page.title = "TACTICAL ASSISTANT v3.0"
        page.bgcolor = COLOR_BG
        page.theme_mode = "dark"
        page.padding = 15
        
        # --- ÉTAT ---
        chat_log = ft.Column(scroll="always", expand=True, spacing=15)
        memory_stack = []
        
        # Chargement historique (Stabilité 100%)
        try:
            stored = page.client_storage.get("tactical_memory")
            if stored:
                memory_stack = json.loads(str(stored))
        except:
            memory_stack = []

        # --- INDICATEUR DE STATUT (Design Radar) ---
        status_indicator = ft.Text(value="[ SYSTEM : STANDBY ]", color="#507080", size=10, font_family="monospace")

        # --- LOGO CYBERNÉTIQUE ---
        brand_logo = ft.Container(
            content=ft.Text(value="T.A", color=COLOR_PRIMARY, weight="bold", size=18),
            width=60, height=60,
            border=ft.border.all(2, COLOR_PRIMARY),
            border_radius=10, # Carré arrondi plus "techno"
            alignment=ft.Alignment(0, 0),
            shadow=ft.BoxShadow(blur_radius=10, color=COLOR_PRIMARY, spread_radius=-5)
        )

        # Affichage mémore
        for msg in memory_stack:
            try:
                r = "ADMIN" if msg.get('role') == 'user' else "CORE"
                t = msg.get('parts', [{}])[0].get('text', '')
                chat_log.controls.append(TacticalMessage(r, t, msg.get('role') == 'user'))
            except: pass

        def run_analysis(prompt, history):
            # Priorité 1 : Gemini (Online)
            try:
                payload = {
                    "contents": history + [{"role": "user", "parts": [{"text": str(prompt)}]}],
                    "system_instruction": {"parts": [{"text": "Tu es un assistant tactique neutre et professionnel. Réponds avec précision."}]}
                }
                # Timeout court pour ne pas bloquer l'app en offline
                res = requests.post(API_URL, json=payload, timeout=7)
                if res.status_code == 200:
                    data = res.json()
                    return str(data['candidates'][0]['content']['parts'][0]['text'])
            except:
                pass
            
            # Priorité 2 : Protocoles de secours (Offline)
            cmd = str(prompt).lower().strip()
            return OFFLINE_PROTOCOLS.get(cmd, OFFLINE_PROTOCOLS["default"])

        def transmit_command(e):
            if not console_input.value: return
            
            cmd_text = str(console_input.value)
            console_input.value = ""
            chat_log.controls.append(TacticalMessage("ADMIN", cmd_text, True))
            status_indicator.value = "[ ANALYSING INPUT... ]"
            status_indicator.color = COLOR_PRIMARY
            page.update()
            
            # Récupération réponse
            response = run_analysis(cmd_text, memory_stack)
            
            # Update Mémoire
            memory_stack.append({"role": "user", "parts": [{"text": cmd_text}]})
            memory_stack.append({"role": "model", "parts": [{"text": response}]})
            
            try:
                # Limitation mémoire pour stabiliser Android
                page.client_storage.set("tactical_memory", json.dumps(memory_stack[-8:]))
            except: pass
            
            status_indicator.value = "[ SYSTEM : READY ]"
            status_indicator.color = "#507080"
            chat_log.controls.append(TacticalMessage("CORE", response, False))
            page.update()

        console_input = ft.TextField(
            hint_text="Saisir protocole...",
            expand=True,
            border_color="#1A3A4F",
            on_submit=transmit_command,
            bgcolor="#081520",
            color=COLOR_TEXT_MAIN,
            text_size=14,
            cursor_color=COLOR_PRIMARY,
            border_width=1,
            focused_border_color=COLOR_PRIMARY
        )

        # Bouton EXECUTE (Custom Cyber Button)
        btn_exec = ft.Container(
            content=ft.Text(value="EXEC", color=COLOR_BG, weight="bold", size=12),
            bgcolor=COLOR_PRIMARY,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=5,
            on_click=transmit_command,
            ink=True
        )

        # --- COMPOSITION PAR COUCHES ---
        page.add(
            # Header
            ft.Row([
                ft.Text(value="TACTICAL_INTERFACE // NODE_01", size=10, color="#507080", font_family="monospace"),
                ft.Container(expand=True),
                ft.Container(width=8, height=8, bgcolor="green", border_radius=4) # Voyant statut
            ]),
            # Logo & Status
            ft.Row([
                brand_logo,
                ft.Column([
                    ft.Text(value="POCKET AI TERMINAL", weight="bold", size=18, color=COLOR_TEXT_MAIN),
                    status_indicator
                ], spacing=2)
            ], alignment="center", spacing=20),
            
            ft.Divider(color="#0F1F2F", thickness=1),
            
            # Zone de Chat
            ft.Container(
                content=chat_log,
                expand=True,
                padding=10,
                border=ft.border.all(1, "#0A1F2F"),
                border_radius=10,
                bgcolor="#050C14"
            ),
            
            # Input
            ft.Container(
                content=ft.Row([console_input, btn_exec], spacing=10),
                padding=ft.padding.only(top=10)
            )
        )

    except Exception as fatal_error:
        # ÉCRAN DE RÉCUPÉRATION TACTIQUE
        page.add(ft.Container(
            content=ft.Column([
                ft.Text(value="FATAL CORE ERROR", color="red", size=22, weight="bold"),
                ft.Text(value=f"TRACE: {str(fatal_error)}", color="white", size=12),
                ft.Text(value="REBOOT REQUIRED", color="#507080", italic=True)
            ]),
            bgcolor="black", expand=True, padding=30
        ))

ft.app(target=main)
