# NextStep Job Manager

NextStep Job Manager is a desktop application designed to help you manage your job applications efficiently. By removing routine actions like copying and renaming every CV and cover letter, it ensures you stay organized throughout your job search process so you have more time for what matters (interview preparation, learning new skills and networking). Also, anything saved in the program available without it. So, you can keep your job searching-related files in your cloud and access them from any device! 

## Features

- **Add Job**: Easily add new job applications with details like position, company, status, resume, cover letter, and more.
- **Edit Job**: Update existing job entries to keep your information current.
- **Delete Job**: Remove job entries that are no longer relevant.
- **Duplicate Job**: Quickly create a copy of an existing job entry.
- **Open Directory**: Access the job's directory directly from the application.
- **Status Tracking**: Track the status of your applications and automatically set the submission date when the status is changed to "Applied".
- **Hide Rejected Applications**: Option to hide rejected applications for a cleaner view.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BorisOskolkov/NextStep.git
   ```
2. Navigate to the project directory:
   ```bash
   cd nextstep
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python job_manager_gui.py
   ```
2. Use the "Add Job" button to add new job application information.
- The resume/CV and cover letter files will be copied to a new directory for future editing!
- The snapshot file will be **moved** for cleaner space on your computer.
3. Right-click on any job entry to edit, delete, duplicate, or open the job directory.
4. Double-click on the status column to change the job status.
5. Click on the company name to open the candidate home link if provided.

## Screenshots

![Main Interface](screenshots/main_interface.png)
![Add Job Dialog](screenshots/add_job_dialog.png)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.

---

Stay organized and take the next step in your career with NextStep!