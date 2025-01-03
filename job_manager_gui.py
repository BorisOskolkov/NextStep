import sys
import csv
import os
import shutil
import datetime

import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, 
    QPushButton, QWidget, QDialog, QFormLayout, QLineEdit, QComboBox, 
    QFileDialog, QMessageBox, QHBoxLayout, QCheckBox, QMenu  
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

CSV_FILE = 'jobs.csv'
JOBS_FOLDER = 'job_positions'
APPLICATION_STATUSES = ["Not started", "Applied", "Interview", "Rejection", "Offer"]

STATUS_COLORS = {
    "Not started": QColor(255, 255, 255),  # White
    "Applied": QColor(173, 216, 230),      # Light Blue
    "Interview": QColor(255, 255, 0),      # Yellow
    "Rejection": QColor(255, 0, 0),        # Red
    "Offer": QColor(0, 255, 0)             # Green
}

def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Position", 
                "Company", 
                "ID", 
                "Snapshot",
                "Status",
                "Resume/CV",
                "Cover Letter",
                "Last Updated",
                "Candidate Home Link",
                "Submitted"  
            ])

def load_jobs():
    jobs = []
    if not os.path.exists(CSV_FILE):
        return jobs

    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            jobs.append(row)
    return jobs

def save_jobs(jobs):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Position", 
            "Company", 
            "ID", 
            "Snapshot", 
            "Status", 
            "Resume/CV", 
            "Cover Letter", 
            "Last Updated",
            "Candidate Home Link",
            "Submitted"  
        ])
        for job in jobs:
            writer.writerow([
                job["Position"],
                job["Company"],
                job["ID"],
                job["Snapshot"],
                job["Status"],
                job["Resume/CV"],
                job["Cover Letter"],
                job["Last Updated"],
                job.get("Candidate Home Link", ""),
                job.get("Submitted", "")])  

def create_job_directory(position_name, company_name, job_id):
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

def rename_job_directory(old_path, new_position_name, new_company_name, new_job_id):
    safe_position_name = new_position_name.replace(" ", "_")
    safe_company_name  = new_company_name.replace(" ", "_")
    safe_job_id        = new_job_id.replace(" ", "_")
    new_dirname = f"{safe_position_name}-{safe_company_name}-{safe_job_id}"
    new_path = os.path.join(JOBS_FOLDER, new_dirname)
    return new_path

class AddJobDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Job")
        self.setGeometry(100, 100, 400, 300)

        self.position_name = QLineEdit()
        self.company_name = QLineEdit()
        self.candidate_home_link = QLineEdit()
        self.job_id = QLineEdit()
        self.link_to_snapshot = QLineEdit()
        self.status = QComboBox()
        self.status.addItems(APPLICATION_STATUSES)
        self.resume_path = ""
        self.cover_letter_path = ""

        form_layout = QFormLayout()
        form_layout.addRow("Position:", self.position_name)
        form_layout.addRow("Company:", self.company_name)
        form_layout.addRow("Candidate Home Link:", self.candidate_home_link)
        form_layout.addRow("Job ID:", self.job_id)

        
        form_layout.addRow("Snapshot:", self.link_to_snapshot)
        self.browse_snapshot_button = QPushButton("Browse Snapshot")
        self.browse_snapshot_button.clicked.connect(self.browse_snapshot)
        form_layout.addRow(self.browse_snapshot_button)

        self.browse_resume_button = QPushButton("Browse")
        self.browse_resume_button.clicked.connect(self.browse_resume)
        form_layout.addRow("Resume/CV:", self.browse_resume_button)  # Add label before button

        self.browse_cover_letter_button = QPushButton("Browse")
        self.browse_cover_letter_button.clicked.connect(self.browse_cover_letter)
        form_layout.addRow("Cover Letter:",self.browse_cover_letter_button)

        form_layout.addRow("Status:", self.status)

        submit_button = QPushButton("Add Job")
        submit_button.setStyleSheet("background-color: green; color: white;")
        submit_button.clicked.connect(self.add_job)
        form_layout.addRow(submit_button)

        self.setLayout(form_layout)

    def browse_resume(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Resume File", "", "Word Files (*.docx);;PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.resume_path = file_path
            self.browse_resume_button.setText(f"Resume/CV: {os.path.basename(file_path)}")

    def browse_snapshot(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Snapshot File", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.link_to_snapshot.setText(file_path)
            self.browse_snapshot_button.setText(f"Snapshot: {os.path.basename(file_path)}")

    def browse_cover_letter(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cover Letter File", "", "Word Files (*.docx);;PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.cover_letter_path = file_path
            self.browse_cover_letter_button.setText(f"Cover Letter: {os.path.basename(file_path)}")

    def add_job(self):
        position_name = self.position_name.text().strip()
        company_name = self.company_name.text().strip()
        candidate_home_link = self.candidate_home_link.text().strip()
        job_id = self.job_id.text().strip()
        link_to_snapshot = self.link_to_snapshot.text().strip()
        status = self.status.currentText()
        resume_path = self.resume_path.strip()
        cover_letter_path = self.cover_letter_path.strip()

        if not position_name or not company_name or not job_id:
            QMessageBox.warning(self, "Warning", "Position, Company, and ID are required.")
            return

        if status not in APPLICATION_STATUSES:
            QMessageBox.warning(self, "Warning", "Invalid application status.")
            return

        date_last_updated = datetime.date.today().strftime("%Y-%m-%d")
        new_job = {
            "Position": position_name,
            "Company": company_name,
            "Candidate Home Link": candidate_home_link,
            "ID": job_id,
            "Snapshot": link_to_snapshot,
            "Status": status,
            "Resume/CV": os.path.basename(resume_path),
            "Cover Letter": cover_letter_path,
            "Last Updated": date_last_updated
        }

        jobs = load_jobs()
        jobs.append(new_job)

        job_dir = create_job_directory(position_name, company_name, job_id)
        if resume_path and os.path.isfile(resume_path):
            try:
                new_resume_path = os.path.join(job_dir, os.path.basename(resume_path))
                shutil.copy2(resume_path, new_resume_path)
                new_job["Resume/CV"] = new_resume_path
            except Exception as e:
                QMessageBox.critical(self, "Error Copying Resume", str(e))

        # Move snapshot file to the new directory
        if link_to_snapshot and os.path.isfile(link_to_snapshot):
            try:
                new_snapshot_path = os.path.join(job_dir, os.path.basename(link_to_snapshot))
                shutil.move(link_to_snapshot, new_snapshot_path)
                new_job["Snapshot"] = new_snapshot_path
            except Exception as e:
                QMessageBox.critical(self, "Error Moving Snapshot", str(e))

        # Copy cover letter to the new directory
        if cover_letter_path and os.path.isfile(cover_letter_path):
            try:
                new_cover_letter = os.path.join(job_dir, os.path.basename(cover_letter_path))
                shutil.copy2(cover_letter_path, new_cover_letter)
                new_job["Cover Letter"] = new_cover_letter
            except Exception as e:
                QMessageBox.critical(self, "Error Copying Cover Letter", str(e))

        save_jobs(jobs)
        self.accept()

class EditJobDialog(QDialog):
    def __init__(self, parent, job, job_dir, row):
        super().__init__(parent)
        self.setWindowTitle("Edit Job")
        self.setGeometry(100, 100, 400, 300)
        self.job = job
        self.job_dir = job_dir
        self.row = row

        self.position_name = QLineEdit(job["Position"])
        self.company_name = QLineEdit(job["Company"])
        self.candidate_home_link = QLineEdit(job.get("Candidate Home Link", ""))
        self.job_id = QLineEdit(job["ID"])
        self.link_to_snapshot = QLineEdit(job["Snapshot"], readOnly=True)
        self.status = QComboBox()
        self.status.addItems(APPLICATION_STATUSES)
        self.status.setCurrentText(job["Status"])
        self.resume_path = job["Resume/CV"]
        self.cover_letter_path = job["Cover Letter"]

        form_layout = QFormLayout()
        form_layout.addRow("Position:", self.position_name)
        form_layout.addRow("Company:", self.company_name)
        form_layout.addRow("Candidate Home Link:", self.candidate_home_link)
        form_layout.addRow("Job ID:", self.job_id)
        form_layout.addRow("Snapshot:", self.link_to_snapshot)
        form_layout.addRow("Status:", self.status)

        self.browse_resume_button = QPushButton(f"Resume/CV: {os.path.basename(self.resume_path)}" if self.resume_path else "Browse Resume")
        self.browse_resume_button.clicked.connect(self.browse_resume)
        form_layout.addRow(self.browse_resume_button)

        self.browse_snapshot_button = QPushButton(f"Snapshot: {os.path.basename(self.link_to_snapshot.text())}" if self.link_to_snapshot.text() else "Browse Snapshot")
        self.browse_snapshot_button.clicked.connect(self.browse_snapshot)
        form_layout.addRow(self.browse_snapshot_button)

        self.browse_cover_letter_button = QPushButton(f"Cover Letter: {os.path.basename(self.cover_letter_path)}" if self.cover_letter_path else "Browse Cover Letter")
        self.browse_cover_letter_button.clicked.connect(self.browse_cover_letter)
        form_layout.addRow(self.browse_cover_letter_button)

        submit_button = QPushButton("Save Changes")
        submit_button.clicked.connect(self.save_changes)
        form_layout.addRow(submit_button)

        self.setLayout(form_layout)

    def browse_resume(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Resume File", "", "PDF Files (*.pdf);;Word Files (*.docx);;All Files (*)")
        if file_path:
            self.resume_path = file_path
            self.browse_resume_button.setText(f"Resume/CV: {os.path.basename(file_path)}")

    def browse_snapshot(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Snapshot File", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.link_to_snapshot.setText(file_path)
            self.browse_snapshot_button.setText(f"Snapshot: {os.path.basename(file_path)}")

    def browse_cover_letter(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cover Letter File", "", "PDF Files (*.pdf);;Word Files (*.docx);;All Files (*)")
        if file_path:
            self.cover_letter_path = file_path
            self.browse_cover_letter_button.setText(f"Cover Letter: {os.path.basename(file_path)}")

    def save_changes(self):
        new_position_name = self.position_name.text().strip()
        new_company_name = self.company_name.text().strip()
        new_candidate_home_link = self.candidate_home_link.text().strip()
        new_job_id = self.job_id.text().strip()
        new_link_to_snapshot = self.link_to_snapshot.text().strip()
        new_status = self.status.currentText()
        new_resume_path = self.resume_path
        new_cover_letter_path = self.cover_letter_path

        if not new_position_name or not new_company_name or not new_job_id:
            QMessageBox.warning(self, "Warning", "Position, Company, and ID are required.")
            return

        if new_status not in APPLICATION_STATUSES:
            QMessageBox.warning(self, "Warning", "Invalid application status.")
            return
        
        old_path = self.job_dir
        new_path = rename_job_directory(self.job_dir, new_position_name, new_company_name, new_job_id)
        print(f"New Job Directory: {new_path}")
        # Update paths to resume and snapshot files before renaming the directory
        resume_path = self.job["Resume/CV"]
        snapshot_path = self.job["Snapshot"]
        cover_letter_path = self.job["Cover Letter"]

        print(f"Checking if resume file exists: {resume_path}")
        if os.path.isfile(resume_path):
            new_resume_path = os.path.join(new_path, os.path.basename(resume_path))
            self.job["Resume/CV"] = new_resume_path
        else:
            print(f"Resume file not found: {resume_path}")

        print(f"Checking if snapshot file exists: {snapshot_path}")
        if os.path.isfile(snapshot_path):
            new_snapshot_path = os.path.join(new_path, os.path.basename(snapshot_path))
            self.job["Snapshot"] = new_snapshot_path
        else:
            print(f"Snapshot file not found: {snapshot_path}")

        print(f"Checking if cover letter file exists: {cover_letter_path}")
        if os.path.isfile(cover_letter_path):
            new_cover_letter_path = os.path.join(new_path, os.path.basename(cover_letter_path))
            self.job["Cover Letter"] = new_cover_letter_path
        else:
            print(f"Cover letter file not found: {cover_letter_path}")

        # Rename the directory after moving the files
        
        
        os.rename(old_path, new_path)
        self.job["Position"] = new_position_name
        self.job["Company"] = new_company_name
        self.job["Candidate Home Link"] = new_candidate_home_link
        self.job["ID"] = new_job_id
        self.job["Snapshot"] = new_link_to_snapshot
        self.job["Status"] = new_status
        self.job["Resume/CV"] = new_resume_path
        self.job["Cover Letter"] = new_cover_letter_path
        self.job["Last Updated"] = datetime.date.today().strftime("%Y-%m-%d")

        jobs = load_jobs()
        jobs[self.row] = self.job
        save_jobs(jobs)
        self.parent().populate_jobs()
        self.accept()

class JobManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NextStep")
        self.setGeometry(100, 100, 1000, 400)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Position", "Company", "ID", "Snapshot", 
            "Status", "Resume/CV", "Cover Letter", "Submitted", "Last Updated"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_status)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)
        self.table.cellClicked.connect(self.cell_clicked)  # Connect cellClicked signal

        add_button = QPushButton("Add Job")
        add_button.setStyleSheet("background-color: green; color: white;")
        add_button.clicked.connect(self.open_add_job_dialog)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.populate_jobs)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)

        self.hide_rejected_checkbox = QCheckBox("Hide Rejected Applications")
        self.hide_rejected_checkbox.stateChanged.connect(self.populate_jobs)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(exit_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.hide_rejected_checkbox)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        initialize_csv()
        self.populate_jobs()

    def open_context_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        duplicate_action = menu.addAction("Duplicate")
        open_directory_action = menu.addAction("Open Directory")

        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        if action == edit_action:
            self.open_edit_job_dialog(self.table.currentRow())
        elif action == delete_action:
            self.delete_job(self.table.currentRow())
        elif action == duplicate_action:
            self.duplicate_job(self.table.currentRow())
        elif action == open_directory_action:
            self.open_job_directory(self.table.currentRow())

    def populate_jobs(self):
        jobs = load_jobs()
        if self.hide_rejected_checkbox.isChecked():
            jobs = [job for job in jobs if job["Status"] != "Rejection"]
        self.table.setRowCount(len(jobs))
        for row, job in enumerate(jobs):
            self.table.setItem(row, 0, QTableWidgetItem(job["Position"]))
            company_item = QTableWidgetItem(job["Company"])
            link = job.get("Candidate Home Link", "")
            if link:
                company_item.setForeground(Qt.blue)
                company_item.setFlags(company_item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                company_item.setData(Qt.UserRole, link)
            self.table.setItem(row, 1, company_item)
            self.table.setItem(row, 2, QTableWidgetItem(job["ID"]))
            
            snapshot_button = QPushButton("Open")
            snapshot_button.clicked.connect(lambda _, path=job["Snapshot"]: self.open_file(path))
            if not job["Snapshot"]:
                snapshot_button.setDisabled(True)
            self.table.setCellWidget(row, 3, snapshot_button)
            
            status_item = QTableWidgetItem(job["Status"])
            status_item.setBackground(STATUS_COLORS.get(job["Status"], QColor(255, 255, 255)))
            self.table.setItem(row, 4, status_item)
            
            resume_button = QPushButton("Open")
            resume_button.clicked.connect(lambda _, path=job["Resume/CV"]: self.open_file(path))
            if not job["Resume/CV"]:
                resume_button.setDisabled(True)
            self.table.setCellWidget(row, 5, resume_button)
            
            cover_letter_button = QPushButton("Open")
            cover_letter_button.clicked.connect(lambda _, path=job["Cover Letter"]: self.open_file(path))
            if not job["Cover Letter"]:
                cover_letter_button.setDisabled(True)
            self.table.setCellWidget(row, 6, cover_letter_button)

            self.table.setItem(row, 7, QTableWidgetItem(job["Last Updated"]))
            self.table.setItem(row, 8, QTableWidgetItem(job.get("Submitted", "")))  # Add Submitted column

        self.table.resizeColumnsToContents()  # Automatically adjust column widths
        self.table.resizeRowsToContents()     # Automatically adjust row heights

        # Adjust the width of the "Status" column to fit the arrow
        self.table.setColumnWidth(4, self.table.columnWidth(4) + 20)

        # Adjust the window width to fit all columns
        total_width = sum(self.table.columnWidth(col) for col in range(self.table.columnCount()))
        self.setFixedWidth(total_width + 65)  # Add some padding

    def open_add_job_dialog(self):
        dialog = AddJobDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.populate_jobs()

    def open_edit_job_dialog(self, row):
        jobs = load_jobs()
        job = jobs[row]
        job_dir = create_job_directory(job["Position"], job["Company"], job["ID"])
        dialog = EditJobDialog(self, job, job_dir, row)
        if dialog.exec_() == QDialog.Accepted:
            self.populate_jobs()

    def delete_job(self, row):
        jobs = load_jobs()
        job = jobs[row]
        job_dir = create_job_directory(job["Position"], job["Company"], job["ID"])

        keep_files_checkbox = QCheckBox("Keep files")
        keep_files_checkbox.setChecked(True)
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("Are you sure you want to delete this job?")
        msg_box.setInformativeText("This action cannot be undone.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setCheckBox(keep_files_checkbox)
        ret = msg_box.exec_()

        if ret == QMessageBox.Yes:
            if not keep_files_checkbox.isChecked():
                shutil.rmtree(job_dir)
            jobs.pop(row)
            save_jobs(jobs)
            self.populate_jobs()

    def duplicate_job(self, row):
        jobs = load_jobs()
        job = jobs[row]

        new_job = job.copy()
        new_job["ID"] = f"{job['ID']}_copy"
        new_job["Last Updated"] = datetime.date.today().strftime("%Y-%m-%d")
        new_job["Submitted"] = ""  # Reset Submitted date

        new_job_dir = create_job_directory(new_job["Position"], new_job["Company"], new_job["ID"])

        if os.path.isfile(job["Resume/CV"]):
            new_resume_path = os.path.join(new_job_dir, os.path.basename(job["Resume/CV"]))
            shutil.copy2(job["Resume/CV"], new_resume_path)
            new_job["Resume/CV"] = new_resume_path

        if os.path.isfile(job["Cover Letter"]):
            new_cover_letter_path = os.path.join(new_job_dir, os.path.basename(job["Cover Letter"]))
            shutil.copy2(job["Cover Letter"], new_cover_letter_path)
            new_job["Cover Letter"] = new_cover_letter_path

        if os.path.isfile(job["Snapshot"]):
            new_snapshot_path = os.path.join(new_job_dir, os.path.basename(job["Snapshot"]))
            shutil.copy2(job["Snapshot"], new_snapshot_path)
            new_job["Snapshot"] = new_snapshot_path

        jobs.append(new_job)
        save_jobs(jobs)
        self.populate_jobs()

    def open_job_directory(self, row):
        jobs = load_jobs()
        job = jobs[row]
        job_dir = create_job_directory(job["Position"], job["Company"], job["ID"])
        if os.path.exists(job_dir):
            os.startfile(job_dir)
        else:
            QMessageBox.warning(self, "Warning", f"Directory not found: {job_dir}")

    def edit_status(self, row, column):
        if column == 4:  # Status column
            combo = QComboBox()
            combo.addItems(APPLICATION_STATUSES)
            combo.setCurrentText(self.table.item(row, column).text())
            self.table.setCellWidget(row, column, combo)
            combo.currentIndexChanged.connect(lambda: self.update_status(row, combo))

    def update_status(self, row, combo):
        new_status = combo.currentText()
        status_item = QTableWidgetItem(new_status)
        status_item.setBackground(STATUS_COLORS.get(new_status, QColor(255, 255, 255)))
        self.table.setItem(row, 4, status_item)
        self.table.removeCellWidget(row, 4)

        jobs = load_jobs()
        job = jobs[row]
        job["Status"] = new_status

        if new_status == "Applied":
            job["Submitted"] = datetime.date.today().strftime("%Y-%m-%d")
            self.table.setItem(row, 7, QTableWidgetItem(job["Submitted"]))  # Update Submitted column
        
        # Update Last Updated field
        job["Last Updated"] = datetime.date.today().strftime("%Y-%m-%d")
        self.table.setItem(row, 8, QTableWidgetItem(job["Last Updated"]))  # Update Last Updated column

        save_jobs(jobs)

    def cell_clicked(self, row, column):
        if column == 1:  # Company column
            item = self.table.item(row, column)
            link = item.data(Qt.UserRole)
            if link:
                webbrowser.open(link)

    def open_file(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            webbrowser.open(path)
        elif os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self, "Warning", f"File not found: {path}")

def main():
    app = QApplication(sys.argv)
    window = JobManagerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()