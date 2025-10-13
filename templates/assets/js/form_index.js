document.getElementById('meuFormulario').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch("{% url 'processar-formulario' %}", {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            document.getElementById('meuFormulario').reset();
        } else {
            alert(data.message);
            // Mostrar erros específicos se necessário
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
});