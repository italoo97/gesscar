console.log('✅ JavaScript está carregando!');

// Aguarde o DOM carregar completamente
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM carregado!');
    
    const form = document.getElementById('meuFormulario');
    
    if (form) {
        console.log('✅ Formulário encontrado!');
        
        form.addEventListener('submit', function(e) {
            console.log('✅ Formulário interceptado!');
            e.preventDefault();
            
            const formData = new FormData(this);
            console.log('Dados:', Object.fromEntries(formData));
            
            fetch("processar-formulario", {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => {
                console.log('Status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Resposta:', data);
                if (data.success) {
                    alert(data.message);
                    this.reset();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao enviar formulário.');
            });
        });
    } else {
        console.log('❌ Formulário NÃO encontrado! Verifique o ID.');
    }
});