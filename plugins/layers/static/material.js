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

    // Add visualization logic
    function visualizeActivationDistributions(data) {
        const ctx = document.getElementById('activationGraph').getContext('2d');
        
        // Process data for visualization
        const datasets = [];
        const colors = ['#4285f4', '#34a853', '#fbbc05', '#ea4335', '#673ab7', '#3f51b5', '#2196f3', '#03a9f4'];
        
        data.forEach((layerPoints, layerIndex) => {
            datasets.push({
                label: `Layer ${layerIndex + 1}`,
                data: layerPoints.map(point => ({x: point[0], y: point[1]})),
                borderColor: colors[layerIndex % colors.length],
                backgroundColor: `${colors[layerIndex % colors.length]}33`,
                pointRadius: 2,
                pointHoverRadius: 4,
                showLine: true, // Connect points with lines
                fill: false
            });
        });

        new Chart(ctx, {
            type: 'scatter',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Token Position',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Attention Weight',
                            font: { size: 14, weight: 'bold' }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { usePointStyle: true }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Layer ${context.datasetIndex + 1}: (${context.parsed.x}, ${context.parsed.y.toFixed(4)})`;
                            }
                        }
                    }
                }
            }
        });

        // Generate insights
        generateInsights(data);
    }

    function generateInsights(data) {
        const insightsContainer = document.getElementById('insights-container');
        
        // Calculate insights
        const layerCount = data.length;
        const avgAttentions = data.map(layer => 
            layer.reduce((sum, point) => sum + point[1], 0) / layer.length
        );
        const maxAttentions = data.map(layer => 
            Math.max(...layer.map(point => point[1]))
        );
        const mostAttentiveLayer = maxAttentions.indexOf(Math.max(...maxAttentions)) + 1;

        // Generate insights HTML
        const insightsHTML = `
            <div class="insights-grid">
                <div class="insight-card">
                    <h6>Number of Layers</h6>
                    <p>${layerCount}</p>
                </div>
                <div class="insight-card">
                    <h6>Most Attentive Layer</h6>
                    <p>Layer ${mostAttentiveLayer}</p>
                </div>
                <div class="insight-card">
                    <h6>Max Attention</h6>
                    <p>${Math.max(...maxAttentions).toFixed(4)}</p>
                </div>
            </div>
            <div class="insight-details">
                <p>• Layer ${mostAttentiveLayer} shows the highest attention weight of ${maxAttentions[mostAttentiveLayer-1].toFixed(4)}</p>
                <p>• Average attention across layers: ${(avgAttentions.reduce((a,b) => a+b) / layerCount).toFixed(4)}</p>
            </div>
        `;
        
        insightsContainer.innerHTML = insightsHTML;
    }

    // Initialize visualization if data is available
    if (window.modelInfo && Array.isArray(window.modelInfo)) {
        visualizeActivationDistributions(window.modelInfo);
        // Setup JSON viewer
        document.getElementById('jsonViewer').textContent = JSON.stringify(window.modelInfo, null, 2);
    }

    // Add JSON viewer toggle
    const toggleJSON = document.getElementById('toggleJSON');
    const jsonViewer = document.getElementById('jsonViewer');
    
    toggleJSON.addEventListener('click', function() {
        const isVisible = jsonViewer.style.display !== 'none';
        jsonViewer.style.display = isVisible ? 'none' : 'block';
        toggleJSON.innerHTML = `<i class="material-icons">${isVisible ? 'visibility' : 'visibility_off'}</i>`;
    });
});
