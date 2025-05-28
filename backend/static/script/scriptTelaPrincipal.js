document.addEventListener('DOMContentLoaded', () => {
    console.log("Page loaded, initializing...");
    mostrarTela('inicio');
    document.querySelectorAll('.exercises-container').forEach(container => {
        container.style.display = 'none';
    });

    document.querySelectorAll('.exercise-circle').forEach(circle => {
        const subtopicoId = circle.getAttribute('data-id');
        const isLocked = circle.classList.contains('locked');
        
        circle.addEventListener('click', () => {
            if (isLocked) {
                console.warn(`Subtema ${subtopicoId} está bloqueado`);
                alert('Este exercício está bloqueado. Conclua o exercício anterior primeiro.');
                return;
            }
            
            if (subtopicoId) {
                console.log(`Redirecting to contentScreen.html?subtopicoId=${subtopicoId}`);
                fetch(`/get_content/${subtopicoId}`)
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(data => {
                                throw new Error(data.error || 'Erro ao acessar o subtema');
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.error) {
                            console.error('Erro ao carregar conteúdo:', data.error);
                            alert(data.error);
                        } else {
                            window.location.href = `/contentScreen.html?subtopicoId=${subtopicoId}`;
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao verificar subtema:', error.message);
                        alert(error.message);
                    });
            } else {
                console.error('No data-id found on clicked circle');
                alert('Erro: Subtema inválido');
            }
        });
    });
});

let updateInterval = null;
const canvas = document.getElementById('chart');
const ctx = canvas ? canvas.getContext('2d') : null;
let state = {
    balance: 0,
    shares: 0,
    current_price: 0,
    price_history: [],
    initial_price: 50.0,
    total_invested: 0,
    mode: 'padrao'
};
let walletState = {
    transactions: [],
    balance: 0,
    total_transactions: 0,
    current_page: 1,
    pages: 1,
    per_page: 10,
    transaction_filter: 'all'
};

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

        if (telaId === 'rank') {
            fetchRanking();
        } else if (telaId === 'simulador-de-investimento') {
            loadInvestmentData();
            startCotaUpdate();
        } else if (telaId === 'carteira-digital') {
            loadWalletHistory();
        } else if (telaId === 'perfil') {
            console.log("Perfil screen selected, data should be rendered via template");
        }
        if (telaId !== 'simulador-de-investimento' && updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
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
        rankItem.style.setProperty('--rank-index', index);

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
            <span class="rank-points">${user.total_pontos} moedas</span>
        `;
        rankingList.appendChild(rankItem);
    });
}

function loadInvestmentData() {
    fetch('/api/state')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error fetching investment data:', data.error);
                alert('Erro ao carregar dados de investimento: ' + data.error);
                return;
            }
            state = { ...state, ...data };
            updateDisplay();
            drawChart();
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert('Erro ao carregar dados de investimento: ' + error.message);
        });
}

function updateDisplay() {
    document.getElementById('balance').textContent = state.balance.toFixed(2);
    document.getElementById('shares').textContent = state.shares;
    document.getElementById('current-price').textContent = state.current_price.toFixed(2);
    const variation = ((state.current_price - state.initial_price) / state.initial_price * 100).toFixed(2);
    document.getElementById('variation').textContent = `${variation}%`;
    document.getElementById('total-invested').textContent = state.total_invested.toFixed(2);
    document.getElementById('current-value').textContent = (state.shares * state.current_price).toFixed(2);
    const lastTwo = state.price_history.slice(-2);
    const trend = lastTwo.length === 2 && lastTwo[1].c > lastTwo[0].c ? 'Subindo' :
                  lastTwo.length === 2 && lastTwo[1].c < lastTwo[0].c ? 'Caindo' : 'Estável';
    document.getElementById('trend').textContent = trend;

    let mensagem = '';
    if (state.mode === 'padrao') {
        mensagem = 'Mercado estável, boas chances de ganhar moedas!';
    } else if (state.mode === 'pico_valorizacao') {
        mensagem = 'As cotas estão subindo! Hora de comprar!';
    } else if (state.mode === 'pico_desvalorizacao') {
        mensagem = 'Cotas em queda, cuidado ao comprar!';
    }
    document.getElementById('message').textContent = mensagem;
}

function handleTrade(action) {
    const amount = parseInt(document.getElementById('amount').value);
    if (isNaN(amount) || amount <= 0) {
        alert('Por favor, insira uma quantidade válida.');
        return;
    }

    fetch('/api/trade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, amount })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert('Erro: ' + data.error);
            } else {
                alert(data.message);
                if (action === 'buy' && !data.error) {
                    state.total_invested += amount * state.current_price;
                }
                loadInvestmentData();
            }
        })
        .catch(error => {
            console.error('Error trading:', error);
            alert('Erro ao processar transação: ' + error.message);
        });
}

function startCotaUpdate() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    loadInvestmentData();
    updateInterval = setInterval(() => {
        fetch('/api/update_price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: state.mode })
        })
        .then(() => loadInvestmentData())
        .catch(error => console.error('Erro ao atualizar preço:', error));
    }, 30000);

    // Atualizar modo a cada 2 minutos (para testes)
    setInterval(() => {
        const modes = ['padrao', 'pico_valorizacao', 'pico_desvalorizacao'];
        const randomMode = modes[Math.floor(Math.random() * modes.length)];
        fetch('/api/set_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: randomMode })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                console.log(data.message);
                state.mode = randomMode;
                loadInvestmentData();
            } else {
                console.error('Error setting mode:', data.error);
            }
        })
        .catch(error => console.error('Erro ao definir modo:', error));
    }, 120000);
}

function drawChart() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const leftPadding = 50;
    const padding = 20;
    const maxEntries = 30;
    const barWidth = (canvas.width - leftPadding - padding) / maxEntries;

    const displayedData = state.price_history.slice(-maxEntries);
    if (displayedData.length === 0) return;

    console.log('Displayed Data:', displayedData);

    const maxPrice = Math.max(...displayedData.map(d => Math.max(d.o, d.c)));
    const minPrice = Math.min(...displayedData.map(d => Math.min(d.o, d.c)));
    const priceRange = maxPrice - minPrice || 1;
    const heightScale = (canvas.height - 2 * padding) / priceRange;

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 5; i++) {
        const y = canvas.height - padding - (i * priceRange / 5) * heightScale;
        ctx.beginPath();
        ctx.moveTo(leftPadding, y);
        ctx.lineTo(canvas.width - padding, y);
        ctx.stroke();
        ctx.fillStyle = 'white';
        ctx.font = '10px Arial';
        ctx.textAlign = 'right';
        ctx.fillText(Math.round(minPrice + (i * priceRange / 5)).toFixed(2), leftPadding - 5, y + 4);
    }

    displayedData.forEach((data, index) => {
        const x = leftPadding + (displayedData.length - 1 - index) * barWidth;
        const openY = canvas.height - padding - (data.o - minPrice) * heightScale;
        const closeY = canvas.height - padding - (data.c - minPrice) * heightScale;
        const height = Math.abs(openY - closeY);

        ctx.fillStyle = data.c >= data.o ? 'rgba(0, 255, 0, 0.7)' : 'rgba(255, 0, 0, 0.7)';
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 1;
        ctx.fillRect(x, Math.min(openY, closeY), barWidth - 2, height);
        ctx.strokeRect(x, Math.min(openY, closeY), barWidth - 2, height);
    });
}

function loadWalletHistory() {
    console.log(`Fetching wallet history for page ${walletState.current_page}, filter: ${walletState.transaction_filter}`);
    const url = `/get_wallet_history?page=${walletState.current_page}&per_page=${walletState.per_page}&type=${walletState.transaction_filter}`;
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error fetching wallet history:', data.error);
                document.getElementById('wallet-history').innerHTML = '<p>Erro ao carregar o histórico da carteira.</p>';
                return;
            }
            walletState.transactions = data.transactions;
            walletState.balance = data.balance;
            walletState.total_transactions = data.total_transactions;
            walletState.pages = data.pages;
            renderWalletHistory();
            updatePagination();
        })
        .catch(error => {
            console.error('Fetch error:', error);
            document.getElementById('wallet-history').innerHTML = '<p>Erro ao carregar o histórico da carteira.</p>';
        });
}

function renderWalletHistory() {
    const walletHistory = document.getElementById('wallet-history');
    walletHistory.innerHTML = '';

    if (walletState.transactions.length === 0) {
        walletHistory.innerHTML = '<p>Nenhuma transação encontrada.</p>';
        return;
    }

    walletState.transactions.forEach(transaction => {
        const transactionItem = document.createElement('div');
        transactionItem.classList.add('wallet-transaction');
        transactionItem.classList.add(transaction.tipo === 'entrada' ? 'transaction-entrada' : 'transaction-saida');

        transactionItem.innerHTML = `
            <span class="transaction-description">${transaction.descricao}</span>
            <span class="transaction-value">${transaction.valor > 0 ? '+' : ''}${transaction.valor.toFixed(2)} moedas</span>
            <span class="transaction-date">${transaction.data_transacao}</span>
        `;
        walletHistory.appendChild(transactionItem);
    });

    document.getElementById('wallet-balance').textContent = walletState.balance.toFixed(2);
}

function updatePagination() {
    const pageDisplay = document.getElementById('wallet-page');
    const prevButton = document.querySelector('.pagination-button[onclick="changeWalletPage(-1)"]');
    const nextButton = document.querySelector('.pagination-button[onclick="changeWalletPage(1)"]');

    pageDisplay.textContent = `Página ${walletState.current_page} de ${walletState.pages}`;
    prevButton.disabled = walletState.current_page === 1;
    nextButton.disabled = walletState.current_page === walletState.pages;
}

function changeWalletPage(direction) {
    const newPage = walletState.current_page + direction;
    if (newPage >= 1 && newPage <= walletState.pages) {
        walletState.current_page = newPage;
        loadWalletHistory();
    }
}

// Adicionar evento ao filtro de transações
document.getElementById('transaction-filter').addEventListener('change', (e) => {
    walletState.transaction_filter = e.target.value;
    walletState.current_page = 1; // Resetar para a primeira página ao mudar o filtro
    loadWalletHistory();
});