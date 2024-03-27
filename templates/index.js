document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('upload-form');
    if(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(this);

            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('prediction-result').textContent = 'Prediction: ' + data.prediction;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
