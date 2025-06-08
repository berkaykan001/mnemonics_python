import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import os
import random

class MnemonicApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Mnemonic Memorization App")
        self.master.geometry("800x600")
        self.master.configure(bg="#f0f0f0")
        
        # Initialize variables first
        self.current_word_data = None
        self.reveal_stage = 0
        self.vocab_data = []
        self.progress_data = {}
        
        # Load vocabulary and progress data
        if not self.load_data():
            return
        
        # Create UI
        self.create_widgets()
        
        # Load first word
        self.load_next_word()
    
    def load_data(self):
        """Load vocabulary and progress data from JSON files"""
        try:
            with open("vocabulary.json", "r", encoding="utf-8-sig") as f:
                self.vocab_data = json.load(f)
            print(f"Successfully loaded {len(self.vocab_data)} words from vocabulary.json")
        except FileNotFoundError:
            messagebox.showerror("Error", "vocabulary.json file not found!")
            return False
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON format in vocabulary.json!\nError details: {str(e)}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error reading vocabulary.json: {str(e)}")
            return False
        
        # Load or create progress data
        self.progress_file = "progress.json"
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    self.progress_data = json.load(f)
            except:
                self.progress_data = {}
        else:
            self.progress_data = {}
        
        # Initialize progress for new words
        for word_data in self.vocab_data:
            word = word_data["word"]
            if word not in self.progress_data:
                self.progress_data[word] = {
                    "interval_days": 1,
                    "last_reviewed": "1970-01-01",
                    "difficulty_level": 1,
                    "times_correct": 0,
                    "times_wrong": 0,
                    "ease_factor": 2.5
                }
        
        return True
    
    def create_widgets(self):
        """Create the main UI elements"""
        # Create main canvas and scrollbar
        canvas = tk.Canvas(self.master, bg="#f0f0f0")
        scrollbar = tk.Scrollbar(self.master, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Now use scrollable_frame instead of main_frame for all widgets
        main_frame = scrollable_frame  # Replace this line and continue with existing code

        # Word label (always visible) - larger and more prominent
        self.word_label = tk.Label(
            main_frame, 
            text="Loading...", 
            font=("Arial", 32, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50",
            wraplength=700,
            height=2
        )
        self.word_label.pack(pady=20, fill="x")
        
        # Translation label
        self.translation_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 18),
            bg="#f0f0f0",
            fg="#27ae60",
            wraplength=700,
            height=2
        )
        self.translation_label.pack(pady=10, fill="x")
        
        # Mnemonic label
        self.mnemonic_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#8e44ad",
            wraplength=700,
            justify="left",
            height=3
        )
        self.mnemonic_label.pack(pady=10, fill="x")
        
        # Image frame
        image_frame = tk.Frame(main_frame, bg="#f0f0f0", height=200)
        image_frame.pack(pady=20, fill="x")
        image_frame.pack_propagate(False)  # Maintain fixed height
        
        self.image_label = tk.Label(image_frame, bg="#f0f0f0", text="")
        self.image_label.pack(expand=True)
        
        # Instruction label
        self.instruction_label = tk.Label(
            main_frame,
            text="Click anywhere to reveal translation, mnemonic, and image",
            font=("Arial", 12, "italic"),
            bg="#f0f0f0",
            fg="#7f8c8d",
            height=2
        )
        self.instruction_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=30)
        
        # Correct button
        self.correct_button = tk.Button(
            button_frame,
            text="✓ CORRECT",
            command=self.correct_answer,
            font=("Arial", 16, "bold"),
            bg="#27ae60",
            fg="white",
            padx=40,
            pady=15,
            relief="raised",
            bd=3,
            width=12
        )
        self.correct_button.pack(side="left", padx=30)
        
        # Wrong button
        self.wrong_button = tk.Button(
            button_frame,
            text="✗ WRONG",
            command=self.wrong_answer,
            font=("Arial", 16, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=40,
            pady=15,
            relief="raised",
            bd=3,
            width=12
        )
        self.wrong_button.pack(side="left", padx=30)
        
        # Progress label at bottom
        self.progress_label = tk.Label(
            main_frame,
            text="Progress will appear here",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d",
            height=2
        )
        self.progress_label.pack(side="bottom", pady=10)
        
        # Bind click events
        self.master.bind("<Button-1>", self.reveal_next)
        self.master.bind("<space>", self.reveal_next)
        self.master.bind("<Return>", self.reveal_next)
        self.master.bind("<Key-1>", lambda e: self.correct_answer())
        self.master.bind("<Key-2>", lambda e: self.wrong_answer())
        
        self.master.focus_set()
        
        # Force update to ensure widgets are drawn
        self.master.update_idletasks()
            # Add mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def reveal_next(self, event=None):
        """Reveal the next piece of information"""
        if self.current_word_data is None:
            return
        
        if self.reveal_stage == 0:
            self.translation_label.config(text=f"Translation: {self.current_word_data['translation']}")
            self.reveal_stage = 1
            self.instruction_label.config(text="Click again to reveal mnemonic")
            
        elif self.reveal_stage == 1:
            self.mnemonic_label.config(text=f"Mnemonic: {self.current_word_data['mnemonic']}")
            self.reveal_stage = 2
            self.instruction_label.config(text="Click again to reveal image")
            
        elif self.reveal_stage == 2:
            self.load_image()
            self.reveal_stage = 3
            self.instruction_label.config(text="Rate your answer using the buttons below")
    
    def load_image(self):
        """Load and display the mnemonic image"""
        if "image" not in self.current_word_data or not self.current_word_data["image"]:
            self.image_label.config(text="[No image available]", image="")
            return
        
        image_path = self.current_word_data["image"]
        try:
            if os.path.exists(image_path):
                pil_image = Image.open(image_path)
                pil_image.thumbnail((250, 250), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo
            else:
                self.image_label.config(text=f"[Image not found: {image_path}]", image="")
        except Exception as e:
            self.image_label.config(text=f"[Error loading image: {str(e)}]", image="")
    
    def get_next_word(self):
        """Select the next word using spaced repetition algorithm"""
        if not self.vocab_data:
            return None
            
        today = datetime.now().date()
        word_priorities = []
        
        for word_data in self.vocab_data:
            word = word_data["word"]
            progress = self.progress_data[word]
            
            last_reviewed = datetime.fromisoformat(progress["last_reviewed"]).date()
            next_review = last_reviewed + timedelta(days=progress["interval_days"])
            days_overdue = (today - next_review).days
            
            priority = (
                days_overdue * 10 +
                progress["times_wrong"] * 5 +
                random.uniform(-2, 2)
            )
            
            word_priorities.append((priority, word_data))
        
        word_priorities.sort(key=lambda x: x[0], reverse=True)
        return word_priorities[0][1]
    
    def load_next_word(self):
        """Load the next word and reset the UI"""
        self.current_word_data = self.get_next_word()
        if self.current_word_data is None:
            self.word_label.config(text="No words available!")
            return
            
        self.reveal_stage = 0
        
        # Reset UI
        self.word_label.config(text=self.current_word_data["word"])
        self.translation_label.config(text="")
        self.mnemonic_label.config(text="")
        self.image_label.config(text="", image="")
        self.instruction_label.config(text="Click anywhere to reveal translation, mnemonic, and image")
        
        # Update progress display
        word = self.current_word_data["word"]
        progress = self.progress_data[word]
        self.progress_label.config(
            text=f"Word: {word} | Correct: {progress['times_correct']} | Wrong: {progress['times_wrong']} | Interval: {progress['interval_days']} days"
        )
    
    def update_progress(self, correct):
        """Update progress data using spaced repetition algorithm"""
        if self.current_word_data is None:
            return
            
        word = self.current_word_data["word"]
        progress = self.progress_data[word]
        today = datetime.now().date()
        
        if correct:
            progress["times_correct"] += 1
            if progress["interval_days"] == 1:
                progress["interval_days"] = 6
            else:
                progress["interval_days"] = int(progress["interval_days"] * progress["ease_factor"])
            progress["ease_factor"] = min(progress["ease_factor"] + 0.1, 3.0)
        else:
            progress["times_wrong"] += 1
            progress["interval_days"] = 1
            progress["ease_factor"] = max(progress["ease_factor"] - 0.2, 1.3)
        
        progress["last_reviewed"] = today.isoformat()
        self.save_progress()
    
    def save_progress(self):
        """Save progress data to file"""
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save progress: {str(e)}")
    
    def correct_answer(self):
        """Handle correct answer"""
        self.update_progress(correct=True)
        self.load_next_word()
    
    def wrong_answer(self):
        """Handle wrong answer"""
        self.update_progress(correct=False)
        self.load_next_word()

def main():
    root = tk.Tk()
    app = MnemonicApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
