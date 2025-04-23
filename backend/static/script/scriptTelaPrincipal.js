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

    // Carregar perfil dinamicamente (se necessário)
    if (document.getElementById('perfil').classList.contains('ativa')) {
        console.log("Perfil screen is active, ensuring data is displayed");
    }
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

        // Carregar ranking se a tela de ranking for selecionada
        if (telaId === 'rank') {
            fetchRanking();
        } else if (telaId === 'perfil') {
            console.log("Perfil screen selected, data should be rendered via template");
        }
    } else {
        console.error(`Screen with ID ${telaId} not found`);
    }
}

function fetchRanking() {
    console.log("Fetching ranking data...");
    fetch('/get_ranking')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error fetching ranking:', data.error);
                document.getElementById('ranking-list').innerHTML = '<p>Erro ao carregar o ranking.</p>';
                return;
            }
            renderRanking(data.ranking);
        })
        .catch(error => {
            console.error('Fetch error:', error);
            document.getElementById('ranking-list').innerHTML = '<p>Erro ao carregar o ranking.</p>';
        });
}

function renderRanking(ranking) {
    const rankingList = document.getElementById('ranking-list');
    rankingList.innerHTML = '';

    ranking.forEach((user, index) => {
        const rankItem = document.createElement('div');
        rankItem.classList.add('ranking-item');

        // Aplicar classes de estilo para os três primeiros
        if (index === 0) {
            rankItem.classList.add('rank-gold');
        } else if (index === 1) {
            rankItem.classList.add('rank-silver');
        } else if (index === 2) {
            rankItem.classList.add('rank-bronze');
        }

        rankItem.innerHTML = `
            <span class="rank-position">${index + 1}º</span>
            <span class="rank-username">${user.username}</span>
            <span class="rank-points">${user.total_pontos} pontos</span>
        `;
        rankingList.appendChild(rankItem);
    });
}