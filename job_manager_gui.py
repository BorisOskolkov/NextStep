import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
import shutil
import datetime

CSV_FILE = 'jobs.csv'
JOBS_FOLDER = 'job_positions'

APPLICATION_STATUSES = ["not started", "applied", "interview", "rejection", "offer"]

def initialize_csv():
    """
    Create the jobs.csv file if it does not exist, with the header row.
    """
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Position Name", 
                "Company Name", 
                "ID", 
                "Link to Snapshot", 
                "Status", 
                "Resume Used", 
                "Cover Letter Used", 
                "Date Last Updated"
            ])

def load_jobs():
    """
    Load the jobs from CSV and return a list of dictionaries.
    """
    jobs = []
    if not os.path.exists(CSV_FILE):
        return jobs

    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            jobs.append(row)
    return jobs

def save_jobs(jobs):
    """
    Overwrite the CSV with the current list of jobs.
    """
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Position Name", 
            "Company Name", 
            "ID", 
            "Link to Snapshot", 
            "Status", 
            "Resume Used", 
            "Cover Letter Used", 
            "Date Last Updated"
        ])
        for job in jobs:
            writer.writerow([
                job["Position Name"],
                job["Company Name"],
                job["ID"],
                job["Link to Snapshot"],
                job["Status"],
                job["Resume Used"],
                job["Cover Letter Used"],
                job["Date Last Updated"]
            ])

def create_job_directory(position_name, company_name, job_id):
    """
    Create a directory in JOBS_FOLDER named "PositionName-CompanyName-ID"
    and return the path.
    """
    if not os.path.exists(JOBS_FOLDER):
        os.makedirs(JOBS_FOLDER)

    safe_position_name = position_name.replace(" ", "_")
    safe_company_name  = company_name.replace(" ", "_")
    safe_job_id        = job_id.replace(" ", "_")
    dirname = f"{safe_position_name}-{safe_company_name}-{safe_job_id}"
    path   = os.path.join(JOBS_FOLDER, dirname)

    if not os.path.exists(path):
        os.makedirs(path)

    return path

class AddJobWindow(tk.Toplevel):
    """
    A pop-up window for adding a new job.
    """
    def __init__(self, parent, refresh_callback):
        super().__init__(parent)
        self.title("Add New Job")
        self.refresh_callback = refresh_callback

        # Window geometry
        self.geometry("400x420")
        self.resizable(False, False)

        # Fields
        self.position_var    = tk.StringVar()
        self.company_var     = tk.StringVar()
        self.id_var          = tk.StringVar()
        self.link_var        = tk.StringVar()
        self.status_var      = tk.StringVar(value=APPLICATION_STATUSES[0])
        self.resume_path_var = tk.StringVar()
        self.cover_var       = tk.StringVar()

        # ========== Widgets ==========
        # Position Name
        tk.Label(self, text="Position Name:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(self, textvariable=self.position_var, width=40).pack(padx=10, pady=3)

        # Company Name
        tk.Label(self, text="Company Name:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(self, textvariable=self.company_var, width=40).pack(padx=10, pady=3)

        # Job ID
        tk.Label(self, text="Job ID:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(self, textvariable=self.id_var, width=40).pack(padx=10, pady=3)

        # Link to Snapshot
        tk.Label(self, text="Link to Snapshot (optional):").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(self, textvariable=self.link_var, width=40).pack(padx=10, pady=3)

        # Status Dropdown
        tk.Label(self, text="Status:").pack(anchor="w", padx=10, pady=(10,0))
        status_menu = ttk.OptionMenu(self, self.status_var, APPLICATION_STATUSES[0], *APPLICATION_STATUSES)
        status_menu.pack(padx=10, pady=3, fill="x")

        # Resume Used
        tk.Label(self, text="Select Resume File:").pack(anchor="w", padx=10, pady=(10,0))
        resume_frame = tk.Frame(self)
        resume_frame.pack(padx=10, pady=3, fill="x")
        tk.Entry(resume_frame, textvariable=self.resume_path_var, width=28).pack(side="left", expand=True, fill="x")
        tk.Button(resume_frame, text="Browse", command=self._browse_resume).pack(side="left", padx=5)

        # Cover Letter
        tk.Label(self, text="Cover Letter (optional):").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(self, textvariable=self.cover_var, width=40).pack(padx=10, pady=3)

        # Submit Button
        tk.Button(self, text="Add Job", command=self._submit).pack(pady=15)

    def _browse_resume(self):
        """
        Open a file dialog for selecting the resume file.
        """
        file_path = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=[("PDF Files", "*.pdf"), ("Word Files", "*.docx"), ("All Files", "*.*")]
        )
        if file_path:
            self.resume_path_var.set(file_path)

    def _submit(self):
        """
        Validate inputs, create job entry, copy resume, save to CSV, close the window.
        """
        position_name = self.position_var.get().strip()
        company_name  = self.company_var.get().strip()
        job_id        = self.id_var.get().strip()
        link_snap     = self.link_var.get().strip()
        status        = self.status_var.get().strip().lower()
        resume_path   = self.resume_path_var.get().strip()
        cover_letter  = self.cover_var.get().strip()

        # Basic Validation
        if not position_name or not company_name or not job_id:
            messagebox.showwarning("Warning", "Position, Company, and ID are required.")
            return

        if status not in APPLICATION_STATUSES:
            messagebox.showwarning("Warning", "Invalid application status.")
            return

        # Prepare new job entry
        date_last_updated = datetime.date.today().strftime("%Y-%m-%d")
        new_job = {
            "Position Name": position_name,
            "Company Name": company_name,
            "ID": job_id,
            "Link to Snapshot": link_snap,
            "Status": status,
            "Resume Used": os.path.basename(resume_path),
            "Cover Letter Used": cover_letter,
            "Date Last Updated": date_last_updated
        }

        # Load existing jobs
        jobs = load_jobs()
        jobs.append(new_job)

        # Create directory for this job
        job_dir = create_job_directory(position_name, company_name, job_id)

        # Copy the resume file (optional if path provided)
        if resume_path and os.path.isfile(resume_path):
            try:
                shutil.copy2(resume_path, job_dir)
            except Exception as e:
                messagebox.showerror("Error Copying Resume", str(e))

        # Save the CSV
        save_jobs(jobs)

        # Refresh the parent table
        self.refresh_callback()

        # Close window
        self.destroy()

class JobSearchGUI(tk.Tk):
    """
    Main window for viewing, refreshing, and adding jobs.
    """
    def __init__(self):
        super().__init__()
        self.title("Job Search Manager (GUI)")
        self.geometry("900x400")

        # Initialize CSV if needed
        initialize_csv()

        # Ensure job_positions folder exists
        if not os.path.exists(JOBS_FOLDER):
            os.makedirs(JOBS_FOLDER)

        # Create UI
        self._create_widgets()
        self._populate_jobs()

    def _create_widgets(self):
        """
        Create the main UI elements: a Treeview for the job table,
        and Buttons for Add Job, Refresh, and Exit.
        """
        # Frame for Treeview
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Create the Treeview
        columns = [
            "Position Name",
            "Company Name",
            "ID",
            "Link to Snapshot",
            "Status",
            "Resume Used",
            "Cover Letter Used",
            "Date Last Updated"
        ]

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            # Adjust the width of columns if desired
            self.tree.column(col, width=120, stretch=True)

        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Frame for Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        add_button = ttk.Button(button_frame, text="Add Job", command=self._open_add_job_window)
        add_button.pack(side="left", padx=5)

        refresh_button = ttk.Button(button_frame, text="Refresh", command=self._populate_jobs)
        refresh_button.pack(side="left", padx=5)

        exit_button = ttk.Button(button_frame, text="Exit", command=self.destroy)
        exit_button.pack(side="right", padx=5)

    def _populate_jobs(self):
        """
        Load jobs from CSV and update the Treeview.
        """
        # Clear current contents
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load jobs
        jobs = load_jobs()

        # Insert into tree
        for job in jobs:
            self.tree.insert("", "end", values=(
                job["Position Name"],
                job["Company Name"],
                job["ID"],
                job["Link to Snapshot"],
                job["Status"],
                job["Resume Used"],
                job["Cover Letter Used"],
                job["Date Last Updated"]
            ))

    def _open_add_job_window(self):
        """
        Open the AddJobWindow pop-up.
        """
        AddJobWindow(self, self._populate_jobs)

def main():
    app = JobSearchGUI()
    app.mainloop()

if __name__ == "__main__":
    main()