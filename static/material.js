document.addEventListener("DOMContentLoaded", function() {
    console.log("Material interactions ready");
    // Additional JavaScript for interactivity

    var modal = document.getElementById('download-plugin-modal');
    var downloadButton = document.getElementById('download-plugin-btn');
    var llmPathInput = document.getElementById('llm-path-input');
    var spinner = document.getElementById('loading-spinner');

    // Check if plugin has been downloaded
    fetch('/check_plugin')
        .then(response => response.json())
        .then(data => {
            if (!data.plugin_downloaded) {
                // Show modal on first launch if plugin not downloaded
                modal.style.display = 'block';
            }
        });

    downloadButton.addEventListener('click', function() {
        var llmPath = llmPathInput.value.trim();
        if (llmPath) {
            // Disable input and button while downloading
            llmPathInput.disabled = true;
            downloadButton.disabled = true;

            // Show the spinner
            spinner.style.display = 'block';

            // Send the LLM path to the server to initiate download
            fetch('/download_plugin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'llm_path': llmPath })
            })
            .then(response => response.json())
            .then(data => {
                // Hide the spinner
                spinner.style.display = 'none';

                if (data.status === 'success') {
                    modal.style.display = 'none';
                    // Reload the page or proceed to open the UI
                    window.location.reload();
                } else {
                    alert('Failed to download Plug-in: ' + data.message);
                    // Re-enable input and button
                    llmPathInput.disabled = false;
                    downloadButton.disabled = false;
                }
            });
        } else {
            alert('Please enter a valid Hugging Face LLM path.');
        }
    });

    var resetButton = document.getElementById('reset-state-btn');

    resetButton.addEventListener('click', function() {
        fetch('/reset_state', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.reload();
            } else {
                alert('Failed to reset state: ' + data.message);
            }
        });
    });

    // Dropdown functionality
    const dropdownButton = document.getElementById('sectionDropdown');
    const dropdownContent = document.getElementById('sectionList');

    dropdownButton.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdownButton.classList.toggle('active');
        dropdownContent.classList.toggle('show');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function() {
        dropdownButton.classList.remove('active');
        dropdownContent.classList.remove('show');
    });

    // Prevent dropdown from closing when clicking inside
    dropdownContent.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Smooth scroll to section when clicking dropdown item
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                // Close dropdown
                dropdownButton.classList.remove('active');
                dropdownContent.classList.remove('show');
                
                // Scroll to section
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Report functionality
    const reportModal = document.getElementById('report-name-modal');
    const downloadReportBtn = document.getElementById('download-report-btn');
    const saveReportBtn = document.getElementById('save-report-btn');
    const reportNameInput = document.getElementById('report-name-input');

    downloadReportBtn.addEventListener('click', function(e) {
        // Check if button is disabled
        if (this.classList.contains('disabled')) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
        reportModal.style.display = 'block';
    });

    // Function to update download report button state
    function updateDownloadReportButton() {
        fetch('/check_report_ready')
            .then(response => response.json())
            .then(data => {
                if (data.ready) {
                    downloadReportBtn.classList.remove('disabled');
                    downloadReportBtn.removeAttribute('disabled');
                    downloadReportBtn.title = "Download analysis report";
                } else {
                    downloadReportBtn.classList.add('disabled');
                    downloadReportBtn.setAttribute('disabled', 'disabled');
                    downloadReportBtn.title = "Please wait for all analyses to complete";
                }
            })
            .catch(error => {
                console.error('Error checking report status:', error);
                downloadReportBtn.classList.add('disabled');
                downloadReportBtn.setAttribute('disabled', 'disabled');
                downloadReportBtn.title = "Error checking report status";
            });
    }

    // Check report readiness periodically
    setInterval(updateDownloadReportButton, 5000);
    // Initial check
    updateDownloadReportButton();

    function closeReportModal() {
        reportModal.style.display = 'none';
    }

    saveReportBtn.addEventListener('click', function() {
        const reportName = reportNameInput.value.trim();
        if (reportName) {
            // Show spinner and disable button
            const spinner = document.getElementById('report-spinner');
            spinner.style.display = 'block';
            saveReportBtn.disabled = true;
            reportNameInput.disabled = true;

            fetch('/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'report_name': reportName })
            })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${reportName}.json`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                // Hide spinner and re-enable inputs
                spinner.style.display = 'none';
                saveReportBtn.disabled = false;
                reportNameInput.disabled = false;
                
                closeReportModal();
            })
            .catch(error => {
                // Hide spinner and re-enable inputs on error
                spinner.style.display = 'none';
                saveReportBtn.disabled = false;
                reportNameInput.disabled = false;
                alert('Error generating report: ' + error);
            });
        } else {
            alert('Please enter a valid report name.');
        }
    });
});
