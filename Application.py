import tkinter as tk
from tkinter import messagebox, Menu
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
import random
import string
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os


class VennDiagramApp:
    def __init__(self, master):
        # Initialize the main application window
        self.master = master
        master.title("Вхід до системи")
        master.geometry("400x600")

        # Counter for diagram generations
        self.diagram_count = 0

        # Create menu bar
        self.menubar = Menu(master)
        master.config(menu=self.menubar)

        # File menu
        file_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новий вхід", command=self.reset_login)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=master.quit)

        # Help menu
        help_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Довідка", menu=help_menu)
        help_menu.add_command(label="Про програму", command=self.show_about)
        help_menu.add_command(label="Допомога", command=self.show_help)

        # Statistics menu
        stats_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Статистика", menu=stats_menu)
        stats_menu.add_command(label="Історія діаграм", command=self.show_diagram_history)

        # Login screen
        self.login_frame = tk.Frame(master)
        self.login_frame.pack(padx=20, pady=20)

        tk.Label(self.login_frame, text="Ім'я:").pack()
        self.name_entry = tk.Entry(self.login_frame)
        self.name_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Прізвище:").pack()
        self.surname_entry = tk.Entry(self.login_frame)
        self.surname_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Номер групи:").pack()
        self.group_entry = tk.Entry(self.login_frame)
        self.group_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Увійти", command=self.check_login).pack(pady=10)

        # Diagram history
        self.diagram_history = []
        self.load_diagram_history()

        # Last used user data
        self.last_name = ""
        self.last_surname = ""
        self.last_group = ""
        self.load_last_user_data()

    def load_last_user_data(self):
        # Load last used user data from JSON file
        if os.path.exists('last_user_data.json'):
            try:
                with open('last_user_data.json', 'r', encoding='utf-8') as f:
                    last_data = json.load(f)
                    self.last_name = last_data.get('name', '')
                    self.last_surname = last_data.get('surname', '')
                    self.last_group = last_data.get('group', '')

                    # Pre-fill entries if data exists
                    self.name_entry.insert(0, self.last_name)
                    self.surname_entry.insert(0, self.last_surname)
                    self.group_entry.insert(0, self.last_group)
            except:
                pass

    def save_last_user_data(self, name, surname, group):
        # Save last used user data to JSON file
        last_data = {
            "name": name,
            "surname": surname,
            "group": group
        }
        with open('last_user_data.json', 'w', encoding='utf-8') as f:
            json.dump(last_data, f, ensure_ascii=False, indent=4)

    def generate_unique_id(self, name, surname, group):
        # Generate or retrieve a consistent unique ID for a user
        for entry in self.diagram_history:
            if (entry['name'] == name and
                    entry['surname'] == surname and
                    entry['group'] == group):
                return entry['unique_id']

        # If no existing ID, generate a new one
        return ''.join(random.choices(string.digits, k=4))

    def check_login(self):
        # Validate login information and create Venn diagram
        name = self.name_entry.get()
        surname = self.surname_entry.get()
        group = self.group_entry.get()

        if name and surname and group:
            # Save last used user data
            self.save_last_user_data(name, surname, group)

            # Generate or retrieve unique ID
            unique_id = self.generate_unique_id(name, surname, group)

            # Find or create entry for this user
            user_entry = next((entry for entry in self.diagram_history
                               if entry['name'] == name and
                               entry['surname'] == surname and
                               entry['group'] == group), None)

            if user_entry:
                # Increment generation attempts
                user_entry['generation_attempts'] = user_entry.get('generation_attempts', 0) + 1
            else:
                # Create new entry if not exists
                user_entry = {
                    "name": name,
                    "surname": surname,
                    "group": group,
                    "unique_id": unique_id,
                    "diagram_number": len(self.diagram_history) + 1,
                    "generation_attempts": 1
                }
                self.diagram_history.append(user_entry)

            # Increment overall diagram count
            self.diagram_count += 1

            # Save updated history
            self.save_diagram_history()

            # Show Venn diagram
            self.show_venn_diagram(name, surname, group, unique_id,
                                   user_entry['generation_attempts'])
        else:
            messagebox.showerror("Помилка", "Заповніть всі поля")

    def show_venn_diagram(self, name, surname, group, unique_id, attempts):
        # Clear current screen
        for widget in self.master.winfo_children():
            if widget != self.menubar:
                widget.destroy()

        # Create frame for diagram
        self.venn_frame = tk.Frame(self.master)
        self.venn_frame.pack(fill=tk.BOTH, expand=True)

        # Create Venn diagram
        fig, ax = plt.subplots(figsize=(6, 4))
        venn = venn3(subsets=(1, 1, 1, 1, 1, 1, 1), set_labels=('A', 'B', 'C'))

        # Initially set all areas to silver
        for subset in ['100', '010', '001', '110', '101', '011', '111']:
            patch = venn.get_patch_by_id(subset)
            if patch:
                patch.set_color('silver')
                patch.set_alpha(0.7)

        # Randomly color 1 or 2 areas grey
        num_areas_to_color = random.randint(1, 2)
        all_areas = ['100', '010', '001', '110', '101', '011', '111']
        areas_to_color = random.sample(all_areas, num_areas_to_color)

        # Color selected areas grey
        for area in areas_to_color:
            if venn.get_patch_by_id(area):
                venn.get_patch_by_id(area).set_color("grey")
                venn.get_patch_by_id(area).set_alpha(0.7)

        # User and diagram information
        info_text = f"Ім'я: {name}\n" \
                    f"Прізвище: {surname}\n" \
                    f"Група: {group}\n" \
                    f"Унікальний ID: {unique_id}\n" \
                    f"Номер діаграми: {self.diagram_count}\n" \
                    f"Кількість спроб: {attempts}"

        tk.Label(self.venn_frame, text=info_text, justify=tk.LEFT, font=('Arial', 10)).pack(pady=10)

        plt.title(f"Діаграма Венна для {name} {surname}")

        # Embed diagram in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.venn_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

        # Buttons frame
        buttons_frame = tk.Frame(self.venn_frame)
        buttons_frame.pack(pady=10)

        # Generate new diagram button
        tk.Button(buttons_frame, text="Згенерувати нову діаграму",
                  command=lambda: self.generate_new_diagram(name, surname, group)).pack(side=tk.LEFT, padx=5)

        # Back to login button
        tk.Button(buttons_frame, text="Назад", command=self.reset_login).pack(side=tk.LEFT, padx=5)

    def generate_new_diagram(self, name, surname, group):
        # Generate a new diagram with the same user data
        unique_id = self.generate_unique_id(name, surname, group)

        # Find user entry and increment attempts
        user_entry = next((entry for entry in self.diagram_history
                           if entry['name'] == name and
                           entry['surname'] == surname and
                           entry['group'] == group), None)

        if user_entry:
            user_entry['generation_attempts'] = user_entry.get('generation_attempts', 0) + 1
            self.save_diagram_history()
            attempts = user_entry['generation_attempts']
        else:
            attempts = 1

        self.diagram_count += 1
        self.show_venn_diagram(name, surname, group, unique_id, attempts)

    def reset_login(self):
        # Return to login screen
        for widget in self.master.winfo_children():
            if widget != self.menubar:
                widget.destroy()

        # Recreate login screen
        self.login_frame = tk.Frame(self.master)
        self.login_frame.pack(padx=20, pady=20)

        tk.Label(self.login_frame, text="Ім'я:").pack()
        self.name_entry = tk.Entry(self.login_frame)
        self.name_entry.insert(0, self.last_name)  # Restore last name
        self.name_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Прізвище:").pack()
        self.surname_entry = tk.Entry(self.login_frame)
        self.surname_entry.insert(0, self.last_surname)  # Restore last surname
        self.surname_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Номер групи:").pack()
        self.group_entry = tk.Entry(self.login_frame)
        self.group_entry.insert(0, self.last_group)  # Restore last group
        self.group_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Увійти", command=self.check_login).pack(pady=10)

    def save_diagram_history(self):
        # Save diagram history to JSON file
        with open('diagram_history.json', 'w', encoding='utf-8') as f:
            json.dump(self.diagram_history, f, ensure_ascii=False, indent=4)

    def load_diagram_history(self):
        # Load diagram history from JSON file
        if os.path.exists('diagram_history.json'):
            with open('diagram_history.json', 'r', encoding='utf-8') as f:
                self.diagram_history = json.load(f)
                # Set counter to last value
                self.diagram_count = len(self.diagram_history)

    def show_diagram_history(self):
        # Create diagram history window
        history_window = tk.Toplevel(self.master)
        history_window.title("Історія діаграм")
        history_window.geometry("400x300")

        # Create text field to display history
        history_text = tk.Text(history_window, wrap=tk.WORD)
        history_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Form history text
        for entry in self.diagram_history:
            history_text.insert(tk.END, f"Номер діаграми: {entry['diagram_number']}\n")
            history_text.insert(tk.END, f"Ім'я: {entry['name']}\n")
            history_text.insert(tk.END, f"Прізвище: {entry['surname']}\n")
            history_text.insert(tk.END, f"Група: {entry['group']}\n")
            history_text.insert(tk.END, f"Унікальний ID: {entry['unique_id']}\n")
            history_text.insert(tk.END, f"Кількість спроб: {entry.get('generation_attempts', 1)}\n\n")

        history_text.config(state=tk.DISABLED)  # Disable editing

    def show_about(self):
        messagebox.showinfo("Про програму", "Додаток для генерації діаграм Венна\n"
                                            "Версія 1.0\n"
                                            "Створено в освітніх цілях")

    def show_help(self):
        messagebox.showinfo("Допомога", "1. Введіть ім'я, прізвище та номер групи\n"
                                        "2. Натисніть 'Увійти'\n"
                                        "3. Буде згенерована унікальна діаграма Венна\n"
                                        "4. Ведеться підрахунок згенерованих діаграм")


def main():
    root = tk.Tk()
    app = VennDiagramApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()