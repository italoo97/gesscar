document.getElementById('meuFormulario').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch(FORM_URL, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(async (response) => {
        if (!response.ok) {
            const text = await response.text();
            throw new Error(`Erro HTTP ${response.status}: ${text}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert(data.message);
            document.getElementById('meuFormulario').reset();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao enviar o formulário.');
    });
});
