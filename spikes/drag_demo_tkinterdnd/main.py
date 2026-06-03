"""
Minimal Drag-and-Drop Spike for TK Lesson Planner (Idea 1 - Playful Pathway)
Framework: Tkinter + tkinterdnd2

Goal: Replicate the core experience — drag colorful ActivityCards
from a left "Library" into a central "Timeline" canvas, reorder them,
and see basic visual feedback (color by domain, duration, snap behavior).

This is a throwaway prototype for framework comparison only.
"""

import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

# ---- Domain colors (pastel, teacher-friendly) ----
DOMAIN_COLORS = {
    "Social-Emotional": "#FFCCE1",   # Soft pink
    "Language": "#CCE5FF",           # Soft blue
    "Mathematics": "#CCFFCC",        # Soft green
    "Science": "#FFFFCC",            # Soft yellow
    "Physical": "#FFCC99",           # Soft orange
    "Arts": "#E0CCFF",               # Soft purple
    "Approaches": "#CCCCCC",         # Neutral gray
}

# ---- Sample seed activities (very small representative set) ----
SEED_ACTIVITIES = [
    {"id": "a1", "title": "Morning Greeting Circle", "domain": "Social-Emotional", "minutes": 10},
    {"id": "a2", "title": "Block Building Challenge", "domain": "Mathematics", "minutes": 20},
    {"id": "a3", "title": "Outdoor Running Games", "domain": "Physical", "minutes": 15},
    {"id": "a4", "title": "Story Time with Puppets", "domain": "Language", "minutes": 12},
    {"id": "a5", "title": "Sensory Bin Exploration", "domain": "Science", "minutes": 18},
    {"id": "a6", "title": "Finger Painting at Art Table", "domain": "Arts", "minutes": 15},
    {"id": "a7", "title": "Free Choice Centers", "domain": "Approaches", "minutes": 25},
]


class ActivityCard(tk.Frame):
    """A single draggable colorful activity card."""
    def __init__(self, master, activity, **kwargs):
        super().__init__(master, **kwargs)
        self.activity = activity
        self.configure(
            bg=DOMAIN_COLORS.get(activity["domain"], "#EEEEEE"),
            highlightthickness=2,
            highlightbackground="#333333",
            padx=8, pady=6
        )

        # Title (prominent)
        tk.Label(
            self,
            text=activity["title"],
            font=("Helvetica", 12, "bold"),
            bg=self["bg"],
            wraplength=160,
            justify="left"
        ).pack(anchor="w")

        # Bottom row: domain + minutes
        bottom = tk.Frame(self, bg=self["bg"])
        bottom.pack(fill="x", pady=(4, 0))

        tk.Label(
            bottom,
            text=f"📚 {activity['domain']}",
            font=("Helvetica", 9),
            bg=self["bg"]
        ).pack(side="left")

        tk.Label(
            bottom,
            text=f"⏱ {activity['minutes']} min",
            font=("Helvetica", 9, "bold"),
            bg=self["bg"]
        ).pack(side="right")

        # Make the whole card draggable
        self._make_draggable()

    def _make_draggable(self):
        """Register as drag source using tkinterdnd2."""
        self.drag_source = self
        self.tk.call(
            "tkdnd::drag_source", "register", self, DND_FILES
        )
        self.bind("<ButtonPress-1>", self._on_drag_start)

    def _on_drag_start(self, event):
        # Set the data that will be dropped (we use the activity id)
        data = self.activity["id"]
        # TkinterDnD way: initiate drag with custom data
        self.tk.call("tkdnd::drag", self, data)


class TimelineSlot(tk.Frame):
    """A droppable slot in the daily timeline."""
    def __init__(self, master, index, on_drop_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.index = index
        self.on_drop_callback = on_drop_callback

        self.configure(
            bg="#F8F8F8",
            relief="groove",
            height=55,
            width=380,
            highlightthickness=1
        )

        self.label = tk.Label(
            self,
            text="Drop activity here →",
            bg="#F8F8F8",
            fg="#888888",
            font=("Helvetica", 9, "italic")
        )
        self.label.pack(expand=True, fill="both")

        # Make this widget a drop target
        self._make_droppable()

    def _make_droppable(self):
        self.tk.call("tkdnd::drop_target", "register", self, DND_FILES)
        self.bind("<<DropEnter>>", self._on_enter)
        self.bind("<<DropLeave>>", self._on_leave)
        self.bind("<<Drop>>", self._on_drop)

        self.drop_target = True

    def _on_enter(self, event):
        self.configure(bg="#E0FFE0")  # Green highlight when hovering
        self.label.configure(bg="#E0FFE0")

    def _on_leave(self, event):
        self.configure(bg="#F8F8F8")
        self.label.configure(bg="#F8F8F8")

    def _on_drop(self, event):
        activity_id = event.data.strip()
        print(f"[Timeline] Dropped activity_id={activity_id} into slot {self.index}")

        # Visual feedback
        self.configure(bg="#FFFACD")  # Pale yellow "just dropped"
        self.after(180, lambda: self.configure(bg="#F8F8F8"))

        # Notify parent to actually place the card
        self.on_drop_callback(self.index, activity_id)


def create_demo_root():
    root = TkinterDnD.Tk()
    root.title("TK Pathway Spike — Tkinter + tkinterdnd2")
    root.geometry("820x520")
    root.minsize(700, 450)

    # ---- Top header ----
    header = tk.Frame(root, bg="#4A6B8A")
    header.pack(fill="x")

    tk.Label(
        header,
        text="Playful Pathway Planner — Drag & Drop Spike (Tkinter)",
        bg="#4A6B8A", fg="white",
        font=("Helvetica", 16, "bold"),
        pady=12
    ).pack()

    # ---- Main layout: 3 columns ----
    main = tk.Frame(root)
    main.pack(fill="both", expand=True, padx=8, pady=8)

    # Left: Library
    lib_frame = tk.Frame(main, width=220)
    lib_frame.pack(side="left", fill="y", padx=(0, 8))

    tk.Label(
        lib_frame,
        text="📚 ACTIVITY LIBRARY",
        font=("Helvetica", 11, "bold")
    ).pack(anchor="w", pady=(0, 6))

    # Scrollable list of cards
    lib_canvas = tk.Canvas(lib_frame, width=200, height=380, highlightthickness=0)
    lib_scroll = ttk.Scrollbar(lib_frame, orient="vertical", command=lib_canvas.yview)
    lib_canvas.configure(yscrollcommand=lib_scroll.set)

    lib_inner = tk.Frame(lib_canvas)
    lib_canvas.create_window((0, 0), window=lib_inner, anchor="nw")

    for act in SEED_ACTIVITIES:
        card = ActivityCard(lib_inner, act)
        card.pack(fill="x", pady=4, padx=4)

    lib_inner.update_idletasks()
    lib_canvas.config(scrollregion=lib_canvas.bbox("all"))
    lib_canvas.pack(side="left", fill="y")
    lib_scroll.pack(side="right", fill="y")

    # Center: Timeline
    timeline_frame = tk.Frame(main)
    timeline_frame.pack(side="left", fill="both", expand=True)

    tk.Label(
        timeline_frame,
        text="🕒 DAILY TIMELINE (drag cards here)",
        font=("Helvetica", 11, "bold")
    ).pack(anchor="w", pady=(0, 6))

    timeline = tk.Frame(timeline_frame)
    timeline.pack(fill="both", expand=True)

    # Create 8 droppable slots (simulating a half-day)
    slots = []
    for i in range(8):
        slot = TimelineSlot(
            timeline,
            index=i,
            on_drop_callback=lambda idx, aid: add_card_to_timeline(timeline, idx, aid)
        )
        slot.pack(pady=2, fill="x")
        slots.append(slot)

    # Right: Instructions + status
    side = tk.Frame(main, width=200)
    side.pack(side="right", fill="y", padx=(8, 0))

    tk.Label(side, text="HOW TO TEST", font=("Helvetica", 10, "bold")).pack(anchor="w")

    instructions = (
        "1. Drag any Activity Card from the left.\n"
        "2. Drop it into one of the timeline slots.\n"
        "3. Watch for highlight + print in terminal.\n"
        "4. Try dropping multiple cards.\n"
        "5. Try to reorder (current simple version just drops).\n\n"
        "Note: This is a minimal spike.\nFull reordering logic comes later."
    )

    tk.Label(
        side,
        text=instructions,
        justify="left",
        font=("Helvetica", 9),
        wraplength=180
    ).pack(anchor="nw", pady=4)

    tk.Label(side, text="Drop target status:", font=("Helvetica", 9, "bold")).pack(anchor="w", pady=(12, 2))
    status_var = tk.StringVar(value="Waiting for first drop...")
    tk.Label(side, textvariable=status_var, fg="#006600", font=("Helvetica", 9)).pack(anchor="w")

    # Footer note
    tk.Label(
        root,
        text="Tkinter + tkinterdnd2 spike  •  Designed for immediate comparison against PySide6 equivalent",
        font=("Helvetica", 8, "italic"), fg="#666666"
    ).pack(side="bottom", pady=4)

    def add_card_to_timeline(parent, slot_index, activity_id):
        # Lookup the activity
        act = next((a for a in SEED_ACTIVITIES if a["id"] == activity_id), None)
        if not act:
            return

        card = ActivityCard(parent, act)
        card.pack(fill="x", pady=1, after=slots[slot_index])  # naive placement

        status_var.set(f"✓ Added '{act['title']}' to slot {slot_index + 1}")
        root.after(2000, lambda: status_var.set("Ready for more drops..."))

    return root


if __name__ == "__main__":
    root = create_demo_root()
    print("=== TK Pathway Planner — Tkinter + tkinterdnd2 SPIKE ===")
    print("Drag cards from left library into timeline slots.")
    print("Watch console + green/yellow visual feedback.")
    root.mainloop()