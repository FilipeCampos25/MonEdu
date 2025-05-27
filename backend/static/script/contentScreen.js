let currentSubtopicoId = null;
let contents = [];
let perguntas = [];
let licaoId = null;
let currentContentIndex = 0;
let userAnswers = {};
let quizSubmitted = false;

function getSubtopicoIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('subtopicoId');
}

function showContentScreen(subtopicoId) {
    currentSubtopicoId = subtopicoId;
    currentContentIndex = 0;
    userAnswers = {};
    quizSubmitted = false;
    console.log(`Fetching content for subtopicoId: ${subtopicoId}`);
    fetch(`/get_content/${subtopicoId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            if (data.error && !data.perguntas.length) {
                console.error('Server error:', data.error);
                alert(data.error);
                return;
            }
            contents = data.conteudos || [];
            perguntas = data.perguntas || [];
            licaoId = data.licao_id;
            if (!licaoId || isNaN(licaoId)) {
                console.error('Erro: licao_id inválido recebido:', data.licao_id);
                alert('Erro: ID da lição inválido. Por favor, tente novamente.');
                return;
            }
            console.log('licaoId definido:', licaoId);
            if (contents.length === 0 && perguntas.length === 0) {
                alert('Nenhum conteúdo ou perguntas disponíveis para este subtema.');
                return;
            }
            displayContent();
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert('Erro ao carregar conteúdo. Verifique a conexão ou tente novamente.');
        });
}

function displayContent() {
    const contentList = document.getElementById('content-list');
    const quizSection = document.getElementById('quiz-section');
    if (!contentList || !quizSection) {
        console.error('Required elements not found');
        return;
    }
    contentList.innerHTML = '';
    quizSection.style.display = 'none';

    if (currentContentIndex < contents.length) {
        const content = contents[currentContentIndex];
        // Escapar caracteres HTML para evitar XSS
        let textoFormatado = content.texto
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            // Substituições de formatação
            .replace(/#([^#]+)#/g, '<h4>$1</h4>')
            .replace(/\*([^*]+)\*/g, '<strong>$1</strong>')
            // Substituir quebras de linha por <br>
            .replace(/\n/g, '<br>');

        contentList.innerHTML = `
            <div class="content-item">
                <h3>${content.numero || ''} - ${content.titulo || 'Sem título'}</h3>
                <div>${textoFormatado}</div>
            </div>
        `;
    } else if (perguntas.length > 0) {
        quizSection.style.display = 'block';
        displayQuiz();
    }
    updateNavigationButtons();
}

function displayQuiz() {
    const quizQuestions = document.getElementById('quiz-questions');
    quizQuestions.innerHTML = '';

    perguntas.forEach((pergunta, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question';

        // Parsear as opções
        const opcoesArray = pergunta.opcoes.split(',').map(opcao => {
            const [letra, texto] = opcao.split(':').map(part => part.trim());
            return { letra, texto };
        });

        let optionsHtml = '';
        opcoesArray.forEach((opcao, i) => {
            const isDisabled = quizSubmitted ? 'disabled' : '';
            const isChecked = userAnswers[pergunta.id_pergunta] === opcao.texto ? 'checked' : '';
            optionsHtml += `
                <li>
                    <input type="radio" name="question${pergunta.id_pergunta}" 
                           value="${opcao.texto}" id="q${pergunta.id_pergunta}_${i}"
                           ${isChecked} ${isDisabled}
                           onchange="saveAnswer(${pergunta.id_pergunta}, this.value)">
                    <label for="q${pergunta.id_pergunta}_${i}" id="label_q${pergunta.id_pergunta}_${i}">
                        ${opcao.letra}: ${opcao.texto}
                    </label>
                </li>
            `;
        });

        questionDiv.innerHTML = `
            <p><strong>Pergunta ${index + 1}:</strong> ${pergunta.enunciado}</p>
            <ul>${optionsHtml}</ul>
        `;
        quizQuestions.appendChild(questionDiv);
    });

    if (quizSubmitted) {
        // Marcar respostas corretas e incorretas
        perguntas.forEach(pergunta => {
            const opcoesArray = pergunta.opcoes.split(',').map(opcao => {
                const [, texto] = opcao.split(':').map(part => part.trim());
                return texto;
            });
            opcoesArray.forEach((opcao, i) => {
                const label = document.getElementById(`label_q${pergunta.id_pergunta}_${i}`);
                if (label) {
                    if (opcao === pergunta.resposta_correta) {
                        label.classList.add('correct');
                    } else if (userAnswers[pergunta.id_pergunta] === opcao && opcao !== pergunta.resposta_correta) {
                        label.classList.add('incorrect');
                    }
                }
            });
        });
    }
}

function saveAnswer(perguntaId, answer) {
    if (!quizSubmitted) {
        userAnswers[perguntaId] = answer;
        console.log('Respostas do usuário:', userAnswers);
    }
}

function submitQuiz() {
    if (quizSubmitted) return;

    const allAnswered = perguntas.every(pergunta => userAnswers[pergunta.id_pergunta]);
    if (!allAnswered) {
        alert('Por favor, responda todas as perguntas antes de enviar.');
        return;
    }

    quizSubmitted = true;
    document.getElementById('submit-quiz').disabled = true;

    // Reexibir o quiz com as marcações
    displayQuiz();

    // Habilitar o botão Próximo
    updateNavigationButtons();
}

function finalizeQuiz() {
    if (!quizSubmitted) {
        console.log('Quiz não enviado. Não é possível finalizar.');
        return;
    }

    if (!licaoId || isNaN(licaoId)) {
        console.error('Erro: licaoId é inválido:', licaoId);
        alert('Erro: ID da lição inválido. Por favor, tente novamente.');
        return;
    }

    let points = 0;
    perguntas.forEach(pergunta => {
        if (userAnswers[pergunta.id_pergunta] === pergunta.resposta_correta) {
            points += 10;
        }
    });

    console.log('Calculando pontos:', { userAnswers, points });

    if (isNaN(points)) {
        console.error('Erro: Pontuação inválida:', points);
        alert('Erro: Pontuação inválida. Por favor, tente novamente.');
        return;
    }

    console.log('Enviando progresso:', { licao_id: licaoId, points: points });

    // Enviar pontos para o servidor
    fetch('/save_progress', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            licao_id: licaoId,
            points: points
        })
    })
        .then(response => {
            console.log('Resposta do servidor:', response.status, response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Erro do servidor:', data.error);
                alert('Erro ao salvar progresso: ' + data.error);
            } else {
                console.log('Progresso salvo:', data);
                window.location.href = data.redirect;
            }
        })
        .catch(error => {
            console.error('Erro ao salvar progresso:', error);
            alert('Erro ao salvar progresso: ' + error.message);
        });
}

function updateNavigationButtons() {
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    if (prevButton && nextButton) {
        prevButton.disabled = currentContentIndex === 0;
        if (currentContentIndex < contents.length) {
            nextButton.disabled = false;
            nextButton.onclick = () => navigateContent(1);
        } else if (perguntas.length > 0 && quizSubmitted) {
            nextButton.disabled = false;
            nextButton.onclick = finalizeQuiz;
        } else {
            nextButton.disabled = !quizSubmitted;
            nextButton.onclick = finalizeQuiz;
        }
    }
}

function navigateContent(direction) {
    currentContentIndex += direction;
    if (currentContentIndex < 0) currentContentIndex = 0;
    if (currentContentIndex > contents.length) currentContentIndex = contents.length;
    displayContent();
}

document.addEventListener('DOMContentLoaded', () => {
    const subtopicoId = getSubtopicoIdFromUrl();
    if (subtopicoId) {
        showContentScreen(subtopicoId);
    } else {
        alert('Nenhum subtema selecionado.');
        window.history.back();
    }
});