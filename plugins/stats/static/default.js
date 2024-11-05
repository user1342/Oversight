document.addEventListener('DOMContentLoaded', function() {
    // Retrieve and display the model info
    const modelInfo = {{ model_info | tojson | safe }};
    const modelInfoContent = document.getElementById('model-info-content');
    modelInfoContent.textContent = JSON.stringify(modelInfo, null, 2);
    
    // Initialize Materialize CSS tooltips
    M.Tooltip.init(document.querySelectorAll('.tooltip'));
});
