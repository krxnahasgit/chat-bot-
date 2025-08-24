import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from datetime import datetime

# -----------------------------
# Elegant Dark-UI Chatbot (Tkinter)
# -----------------------------
# - Single file
# - Offline
# - Dark theme, bubble styles, smooth scrolling
# - Enter to send, Shift+Enter for new line
# -----------------------------

class ChatbotApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---------- THEME ----------
        self.title("Chatbot")
        self.geometry("720x560")
        self.minsize(560, 480)

        # Palette (Grok-ish vibe)
        self.COL_BG        = "#0b0e14"   # window bg
        self.COL_PANEL     = "#0f141a"   # chat panel bg
        self.COL_USER      = "#2563eb"   # user bubble
        self.COL_BOT       = "#1f2937"   # bot bubble
        self.COL_TEXT_MAIN = "#e5e7eb"   # main text
        self.COL_SUBTLE    = "#9aa4b2"   # timestamps/placeholder
        self.COL_ACCENT    = "#22c55e"   # send button
        self.COL_ACCENT_H  = "#16a34a"   # send hover

        self.configure(bg=self.COL_BG)

        # Fonts
        self.font_body = tkfont.Font(family="Segoe UI", size=11)
        self.font_mono = tkfont.Font(family="Cascadia Code", size=10)
        self.font_small = tkfont.Font(family="Segoe UI", size=9)

        # ---------- LAYOUT ----------
        # Header
        header = tk.Frame(self, bg=self.COL_BG)
        header.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(
            header, text="🤖  Offline GUI Chatbot",
            bg=self.COL_BG, fg=self.COL_TEXT_MAIN, font=("Segoe UI Semibold", 14)
        ).pack(side="left")
        tk.Label(
            header, text="Grok-style minimal UI", bg=self.COL_BG,
            fg=self.COL_SUBTLE, font=self.font_small
        ).pack(side="left", padx=(8,0))

        # Chat container (scrollable)
        outer = tk.Frame(self, bg=self.COL_BG)
        outer.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.canvas = tk.Canvas(outer, bg=self.COL_PANEL, highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y", padx=(6,0))
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.chat_frame = tk.Frame(self.canvas, bg=self.COL_PANEL)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw", width=1)
        self.canvas.bind("<Configure>", self._resize_chat_width)

        # Input bar
        input_bar = tk.Frame(self, bg=self.COL_BG)
        input_bar.pack(fill="x", padx=12, pady=(0, 12))

        self.entry = tk.Text(input_bar, height=2, wrap="word",
                             bg="#0c1117", fg=self.COL_TEXT_MAIN,
                             insertbackground=self.COL_TEXT_MAIN,
                             relief="flat", padx=10, pady=8)
        self.entry.configure(font=self.font_body)
        self.entry.pack(side="left", fill="both", expand=True)
        self.entry.bind("<Return>", self._send_on_enter)
        self.entry.bind("<Shift-Return>", lambda e: None)  # allow newline with Shift+Enter
        self._set_placeholder("Type a message…  (Enter to send, Shift+Enter for new line)")

        self.send_btn = tk.Button(
            input_bar, text="Send", command=self.on_send,
            bg=self.COL_ACCENT, fg="white", activebackground=self.COL_ACCENT_H,
            activeforeground="white", relief="flat", padx=16, pady=10, cursor="hand2"
        )
        self.send_btn.pack(side="left", padx=(10, 0))
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.configure(bg=self.COL_ACCENT_H))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.configure(bg=self.COL_ACCENT))

        # ---------- BOT LOGIC (simple, offline) ----------
        self.intents = [
            (("hello", "hi", "hey"), "Hello! How can I help you today?"),
            (("how are", "how’s it going"), "I’m doing great! What can I do for you?"),
            (("your name", "who are you"), "I’m a Tkinter chatbot with a sleek dark UI."),
            (("time", "date"), lambda: f"It’s {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
            (("bye", "goodbye", "exit"), "See you later!")
        ]
        self.default_reply = "Hmm, I didn’t quite catch that. Try rephrasing?"

        # First message
        self.add_bot("Hi! I’m your offline GUI chatbot. Ask me something, or try “time”.")
        self.after(200, lambda: self.entry.focus_set())

    # --------- UI Helpers ---------
    def _resize_chat_width(self, event):
        # Keep bubbles full width minus paddings
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _scroll_to_bottom(self):
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _send_on_enter(self, event):
        # Enter sends; Shift+Enter inserts newline
        if event.state & 0x0001:  # Shift
            return
        self.on_send()
        return "break"

    def _set_placeholder(self, text):
        self.entry.insert("1.0", text)
        self.entry.configure(fg=self.COL_SUBTLE)
        def on_focus_in(_):
            if self.entry.get("1.0", "end-1c") == text:
                self.entry.delete("1.0", "end")
                self.entry.configure(fg=self.COL_TEXT_MAIN)
        def on_focus_out(_):
            if not self.entry.get("1.0", "end-1c").strip():
                self.entry.insert("1.0", text)
                self.entry.configure(fg=self.COL_SUBTLE)
        self.entry.bind("<FocusIn>", on_focus_in)
        self.entry.bind("<FocusOut>", on_focus_out)

    # --------- Message Bubbles ---------
    def _bubble(self, who: str, text: str):
        # Row container
        row = tk.Frame(self.chat_frame, bg=self.COL_PANEL)
        row.pack(fill="x", padx=14, pady=6)

        # Bubble frame
        is_user = (who == "You")
        bubble_bg = self.COL_USER if is_user else self.COL_BOT
        anchor_side = "e" if is_user else "w"

        bubble = tk.Frame(row, bg=bubble_bg)
        bubble.pack(side=("right" if is_user else "left"), anchor=anchor_side)

        # Name / timestamp (subtle)
        meta = tk.Label(bubble, text=who, bg=bubble_bg, fg="#e6eefc" if is_user else self.COL_SUBTLE,
                        font=("Segoe UI", 9, "bold"))
        meta.pack(anchor=("e" if is_user else "w"), padx=10, pady=(8, 0))

        lbl = tk.Label(
            bubble, text=text, wraplength=520,
            justify=("right" if is_user else "left"),
            bg=bubble_bg, fg="white" if is_user else self.COL_TEXT_MAIN,
            font=self.font_body
        )
        lbl.pack(padx=10, pady=(2, 8))

        # A little padding to “round” feel
        bubble.configure(padx=2, pady=2)
        self._scroll_to_bottom()

    def add_user(self, text: str):
        self._bubble("You", text)

    def add_bot(self, text: str):
        self._bubble("Bot", text)

    # --------- Chat Logic ---------
    def _reply_for(self, user_text: str) -> str:
        t = user_text.lower().strip()
        for keys, reply in self.intents:
            if any(k in t for k in keys):
                return reply() if callable(reply) else reply
        return self.default_reply

    def on_send(self):
        raw = self.entry.get("1.0", "end-1c")
        text = raw.strip()
        if not text:
            return
        self.entry.delete("1.0", "end")
        self.add_user(text)
        self.after(120, lambda: self.add_bot(self._reply_for(text)))


if __name__ == "__main__":
    app = ChatbotApp()
    app.mainloop()
