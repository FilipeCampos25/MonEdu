document.addEventListener('DOMContentLoaded', () => {
    console.log("Page loaded, initializing...");
    mostrarTela('inicio');
    document.querySelectorAll('.exercises-container').forEach(container => {
        container.style.display = 'none';
    });

    // Adicionar listeners para os círculos
    document.querySelectorAll('.exercise-circle').forEach(circle => {
        const subtopicoId = circle.getAttribute('data-id');
        circle.addEventListener('click', () => {
            if (subtopicoId) {
                console.log(`Redirecting to contentScreen.html?subtopicoId=${subtopicoId}`);
                window.location.href = `/contentScreen.html?subtopicoId=${subtopicoId}`;
            } else {
                console.error('No data-id found on clicked circle');
                alert('Erro: Subtema inválido');
            }
        });
    });
});

function toggleExercises(exerciseId) {
    console.log(`Toggling exercises for ${exerciseId}`);
    const exercises = document.getElementById(exerciseId);
    if (exercises) {
        const isVisible = exercises.style.display === 'flex';
        exercises.style.display = isVisible ? 'none' : 'flex';
        if (!isVisible) {
            exercises.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    } else {
        console.error(`Exercises container with ID ${exerciseId} not found`);
    }
}

function mostrarTela(telaId) {
    console.log(`Showing screen: ${telaId}`);
    const telas = document.querySelectorAll('.tela');
    telas.forEach(tela => {
        tela.classList.remove('ativa');
    });
    const telaSelecionada = document.getElementById(telaId);
    if (telaSelecionada) {
        telaSelecionada.classList.add('ativa');
        const headerHeight = document.querySelector('.header-container').offsetHeight;
        window.scrollTo({
            top: telaSelecionada.offsetTop - headerHeight,
            behavior: 'smooth'
        });
    } else {
        console.error(`Screen with ID ${telaId} not found`);
    }
}