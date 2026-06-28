const API = "https://muraldisc-main.onrender.com";

let currentUserId = null;

// Função para iniciar o login
function loginDiscord() {
    window.location.href = `${API}/login`;
}

async function loadProfile() {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');

    const loginSection = document.getElementById("login-section");
    const profileSection = document.getElementById("profile-section");

    if (!userId) {
        loginSection.style.display = "flex";
        profileSection.style.display = "none";
        return;
    }

    try {
        const response = await fetch(`${API}/users/${userId}`);
        const user = await response.json();

        if (user.error) {
            alert("Usuário não encontrado!");
            loginSection.style.display = "flex";
            profileSection.style.display = "none";
            return;
        }

        currentUserId = user.id;

        document.getElementById("username").innerText = user.global_name || user.username;
        document.getElementById("bio").innerText = user.bio || "Sem biografia.";

        if (user.avatar) {
            document.getElementById("avatar").src = user.avatar;
        }

        loginSection.style.display = "none";
        profileSection.style.display = "block";

        loadComments(currentUserId);
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar o perfil. Verifique se o backend está rodando.");
    }
}

async function loadComments(userId) {
    const response = await fetch(`${API}/comments/${userId}`);
    const comments = await response.json();
    const commentsDiv = document.getElementById("comments");

    commentsDiv.innerHTML = "";

    if (comments.length === 0) {
        commentsDiv.innerHTML = "<p class='no-comments'>Nenhum comentário ainda. Seja o primeiro!</p>";
        return;
    }

    comments.forEach(comment => {
        commentsDiv.innerHTML += `
            <div class="comment">
                <div class="comment-author">${comment.author}</div>
                <div class="comment-content">${comment.content}</div>
            </div>
        `;
    });
}

async function sendComment() {
    const author = document.getElementById("author").value.trim();
    const content = document.getElementById("commentText").value.trim();

    if (!author || !content) {
        alert("Preencha todos os campos");
        return;
    }

    const btn = document.querySelector(".comment-form button");
    btn.innerText = "Enviando...";
    btn.disabled = true;

    try {
        const response = await fetch(`${API}/comments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: currentUserId,
                author_name: author,
                content: content
            })
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById("author").value = "";
            document.getElementById("commentText").value = "";
            loadComments(currentUserId);
        } else {
            alert("Erro ao enviar comentário.");
        }
    } catch (err) {
        console.error(err);
        alert("Erro de conexão.");
    } finally {
        btn.innerText = "Enviar Comentário";
        btn.disabled = false;
    }
}

loadProfile();