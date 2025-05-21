const elemento1 = document.getElementById('login');
const elemento2 = document.getElementById('cadastro');
const formLogin = document.querySelector('.log');
const formCadastro = document.querySelector('.cad');

elemento2.style.filter = 'blur(30px)';
formLogin.classList.add('revelado');

function Blurlogin() {
    elemento1.style.filter = 'blur(30px)';
    elemento2.style.filter = 'none';
    formLogin.classList.remove('revelado');
    formCadastro.classList.add('revelado');
}

function Blurcadastro() {
    elemento2.style.filter = 'blur(30px)';
    elemento1.style.filter = 'none';
    formCadastro.classList.remove('revelado');
    formLogin.classList.add('revelado');
}

function subirTelaInicio() {
    const overlay = document.getElementById('inicio');
    overlay.classList.add('hidden');
}
