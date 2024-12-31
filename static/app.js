function displayPDFNames() {
    const fileInput = document.getElementById('pdf_files');
    const fileList = document.getElementById('uploaded_files_list');
    fileList.innerHTML = ''; // Clear the list before displaying

    for (let i = 0; i < fileInput.files.length; i++) {
        const listItem = document.createElement('li');
        listItem.textContent = fileInput.files[i].name; // Display the file name
        fileList.appendChild(listItem);
    }
}

function processPDF() {
    const formData = new FormData();
    const fileInput = document.getElementById('pdf_files');
    const processingStatus = document.getElementById('processing_status');
    processingStatus.textContent = ''; // Clear previous status

    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append('pdf_files', fileInput.files[i]);
    }

    fetch('/process_pdf', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            processingStatus.textContent = 'Processing done ✅'; // Show processing status
        })
        .catch(error => {
            console.error('Error:', error);
            processingStatus.textContent = 'Error processing files ❌'; // Show error status
        });
}

function askQuestion() {
    const question = document.getElementById('question').value;
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerHTML = `<p>${data.response || "The answer is not available in the context."}</p>`;
    })
    .catch(error => console.error('Error:', error));
}

