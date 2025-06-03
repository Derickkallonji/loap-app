document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loanApplicationForm');

    function validateForm() {
        let isValid = true;

        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = 'red';
            } else {
                field.style.borderColor = '#ccc';
            }
        });

        const email = form.querySelector('#email');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email.value && !emailRegex.test(email.value)) {
            isValid = false;
            email.style.borderColor = 'red';
            alert('Please enter a valid email address.');
        }

        const phone = form.querySelector('#phone');
        const phoneRegex = /^\d{10,}$/;
        if (phone.value && !phoneRegex.test(phone.value)) {
            isValid = false;
            phone.style.borderColor = 'red';
            alert('Please enter a valid phone number (digits only, at least 10 digits).');
        }

        const videoInput = form.querySelector('#videoConfirmation');
        const bankStatementsInput = form.querySelector('#bankStatements');

        if (videoInput.files.length > 0) {
            const videoFile = videoInput.files[0];
            if (videoFile.size > 10 * 1024 * 1024 * 1024) {
                isValid = false;
                alert('Video file size must not exceed 10 GB.');
                videoInput.style.borderColor = 'red';
            }
        }

        if (bankStatementsInput.files.length > 0) {
            for (let file of bankStatementsInput.files) {
                if (file.size > 100 * 1024 * 1024) {
                    isValid = false;
                    alert('Bank statement/Payslip file size must not exceed 100 MB per file.');
                    bankStatementsInput.style.borderColor = 'red';
                    break;
                }
                if (!file.name.endsWith('.pdf')) {
                    isValid = false;
                    alert('Bank statements and payslips must be PDF files.');
                    bankStatementsInput.style.borderColor = 'red';
                }
            }
        }

        return isValid;
    }

    function handleSubmit(event) {
        event.preventDefault();

        if (validateForm()) {
            const formData = new FormData(form);

            fetch('/submit', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Error: ${data.error}`);
                } else {
                    alert('Form submitted successfully! Check the server logs for details.');
                    form.reset();
                }
            })
            .catch(error => {
                alert('An error occurred while submitting the form.');
                console.error('Error:', error);
            });
        } else {
            alert('Please fill in all required fields correctly and ensure files meet size requirements.');
        }
    }

    form.querySelectorAll('input[required]').forEach(input => {
        input.addEventListener('input', function () {
            if (this.value.trim()) {
                this.style.borderColor = '#ccc';
            }
        });
    });

    form.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function () {
            if (this.files.length > 0) {
                this.style.borderColor = '#ccc';
            }
        });
    });
});