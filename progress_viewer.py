import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class ProgressViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("Vocabulary Progress Viewer")
        self.master.geometry("1000x600")

        self.progress_data = {}
        self.sort_column = None
        self.sort_reverse = False

        if not self.load_data():
            return

        self.create_widgets()
        self.populate_table()

    def load_data(self):
        """Load progress data from JSON file"""
        try:
            with open("progress.json", "r", encoding="utf-8") as f:
                self.progress_data = json.load(f)
            return True
        except FileNotFoundError:
            tk.messagebox.showerror("Error", "progress.json file not found!")
            return False
        except json.JSONDecodeError as e:
            tk.messagebox.showerror("Error", f"Invalid JSON format: {e}")
            return False

    def create_widgets(self):
        """Create the table view with scrollbars"""
        # Summary frame at top
        summary_frame = tk.Frame(self.master, bg="#f0f0f0", pady=10)
        summary_frame.pack(fill="x")

        total_words = len(self.progress_data)
        total_correct = sum(p["times_correct"] for p in self.progress_data.values())
        total_wrong = sum(p["times_wrong"] for p in self.progress_data.values())

        summary_text = f"Total Words: {total_words}  |  Total Correct: {total_correct}  |  Total Wrong: {total_wrong}"
        summary_label = tk.Label(
            summary_frame,
            text=summary_text,
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        summary_label.pack()

        # Table frame
        table_frame = tk.Frame(self.master)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Define columns
        columns = ("word", "interval", "last_reviewed", "correct", "wrong", "ease_factor", "next_review")

        # Create Treeview
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Define column headings and widths
        column_config = {
            "word": ("Word", 200),
            "interval": ("Interval (days)", 100),
            "last_reviewed": ("Last Reviewed", 120),
            "correct": ("Correct", 80),
            "wrong": ("Wrong", 80),
            "ease_factor": ("Ease Factor", 100),
            "next_review": ("Next Review", 120)
        }

        for col, (heading, width) in column_config.items():
            self.tree.heading(col, text=heading, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, anchor="center")

        # Word column should be left-aligned
        self.tree.column("word", anchor="w")

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Style configuration
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        # Alternating row colors
        self.tree.tag_configure("oddrow", background="#f9f9f9")
        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("overdue", background="#ffcccc")
        self.tree.tag_configure("due_soon", background="#ffffcc")

    def populate_table(self):
        """Fill the table with progress data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        today = datetime.now().date()

        for idx, (word, progress) in enumerate(self.progress_data.items()):
            last_reviewed = datetime.fromisoformat(progress["last_reviewed"]).date()
            next_review = last_reviewed + __import__("datetime").timedelta(days=progress["interval_days"])
            days_until = (next_review - today).days

            # Format next review
            if days_until < 0:
                next_review_str = f"{abs(days_until)} days overdue"
                tag = "overdue"
            elif days_until == 0:
                next_review_str = "Today"
                tag = "due_soon"
            elif days_until == 1:
                next_review_str = "Tomorrow"
                tag = "due_soon"
            else:
                next_review_str = next_review.strftime("%Y-%m-%d")
                tag = "oddrow" if idx % 2 else "evenrow"

            values = (
                word,
                progress["interval_days"],
                progress["last_reviewed"],
                progress["times_correct"],
                progress["times_wrong"],
                f"{progress['ease_factor']:.2f}",
                next_review_str
            )

            self.tree.insert("", "end", values=values, tags=(tag,))

    def sort_by_column(self, column):
        """Sort the table by the clicked column"""
        # Toggle sort direction if same column clicked
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # Get all items
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children("")]

        # Determine sort key based on column type
        def sort_key(item):
            value = item[0]
            if column in ("interval", "correct", "wrong"):
                return int(value) if value else 0
            elif column == "ease_factor":
                return float(value) if value else 0.0
            elif column == "next_review":
                # Handle special strings
                if "overdue" in value:
                    days = int(value.split()[0])
                    return -days  # Negative for overdue
                elif value == "Today":
                    return 0
                elif value == "Tomorrow":
                    return 1
                else:
                    try:
                        return (datetime.strptime(value, "%Y-%m-%d").date() - datetime.now().date()).days
                    except:
                        return 999
            else:
                return value.lower()

        items.sort(key=sort_key, reverse=self.sort_reverse)

        # Rearrange items in sorted order
        for idx, (_, item) in enumerate(items):
            self.tree.move(item, "", idx)

        # Update row colors after sorting
        for idx, item in enumerate(self.tree.get_children("")):
            current_tags = self.tree.item(item, "tags")
            # Preserve overdue/due_soon tags
            if "overdue" in current_tags or "due_soon" in current_tags:
                continue
            new_tag = "oddrow" if idx % 2 else "evenrow"
            self.tree.item(item, tags=(new_tag,))

        # Update column header to show sort direction
        for col in ("word", "interval", "last_reviewed", "correct", "wrong", "ease_factor", "next_review"):
            heading_text = {
                "word": "Word",
                "interval": "Interval (days)",
                "last_reviewed": "Last Reviewed",
                "correct": "Correct",
                "wrong": "Wrong",
                "ease_factor": "Ease Factor",
                "next_review": "Next Review"
            }[col]

            if col == column:
                arrow = " ▼" if self.sort_reverse else " ▲"
                self.tree.heading(col, text=heading_text + arrow)
            else:
                self.tree.heading(col, text=heading_text)


def main():
    root = tk.Tk()
    app = ProgressViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
