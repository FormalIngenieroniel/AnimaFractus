// --- ESTADO GLOBAL ---
let appData = null; // Guardará la respuesta de la IA
let currentBook = null; // Agente seleccionado
let currentPage = 0;
const CHARS_PER_PAGE = 700;

// --- MOMENTO 1 -> 2: START ANALYSIS ---
async function startAnalysis() {
    const query = document.getElementById('userQuery').value;
    const btn = document.getElementById('startBtn');
    
    if (!query) return alert("Por favor ingresa una pregunta.");

    // UI Loading
    btn.innerText = "Convocando Agentes...";
    btn.disabled = true;
    btn.style.cursor = "wait";

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ question: query })
        });
        
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        appData = data; // Guardamos datos nuevos
        
        // Transición a Momento 2 (Mostrar Libros)
        document.getElementById('books-container').classList.remove('hidden');
        
        // --- HABILITAR MÚLTIPLES CONSULTAS ---
        btn.innerText = "Nueva Consulta"; 
        btn.disabled = false;
        btn.style.cursor = "pointer";
        
        const mainTitle = document.querySelector('.main-title');
        mainTitle.style.color = "#4caf50";
        setTimeout(() => { mainTitle.style.color = ""; }, 500);
        
    } catch (error) {
        alert("Error: " + error.message);
        btn.innerText = "Reintentar";
        btn.disabled = false;
        btn.style.cursor = "pointer";
    }
}

// --- MOMENTO 2 -> 3: ABRIR LIBRO ---
function openBook(agentName) {
    if (!appData) return alert("Primero debes comenzar el debate.");

    currentBook = agentName;
    currentPage = 0;

    // 1. Configurar Portada
    const coverImg = document.getElementById('cover-img');
    const safeName = agentName.toLowerCase().replace(' ', '_');
    
    // Rutas dinámicas
    coverImg.src = `/static/images/bk_${safeName}_f.png`;
    // Fallback simple por si falla la imagen
    coverImg.onerror = () => { console.log("Imagen portada no encontrada"); };

    const backImg = document.getElementById('back-img');
    backImg.src = `/static/images/bk_${safeName}_b.png`;

    // 2. PREPARAR IMAGEN DE LAS PÁGINAS (CONTENIDO)
    // Aquí es donde inyectamos la imagen de fondo "pixel art" para el texto
    const pagePaper = document.querySelector('.page-paper');
    // Usamos la convención bk_[nombre]_p.png
    pagePaper.style.backgroundImage = `url('/static/images/bk_${safeName}_p.png')`;

    // Mostrar Overlay y vista de portada
    document.getElementById('book-overlay').classList.remove('hidden');
    switchView('view-cover');
}

// --- HELPERS DE VISTA ---
function switchView(viewId) {
    document.querySelectorAll('.book-view').forEach(el => el.classList.add('hidden'));
    document.getElementById(viewId).classList.remove('hidden');
}

function closeBook() {
    document.getElementById('book-overlay').classList.add('hidden');
    currentBook = null;
}

// --- MOMENTO 3 -> 4: CONTENIDO ---
function goToContent(fromBack = false) {
    let fullText = "";
    let ragDocs = [];

    if (currentBook === "The Historian") {
        fullText = appData.synthesis;
    } else {
        const log = appData.logs.find(l => l.agent === currentBook);
        if (log) {
            fullText = log.thought;
            ragDocs = log.context_used || [];
        } else {
            fullText = "Error: Datos no encontrados para este agente.";
        }
    }

    const totalPages = Math.ceil(fullText.length / CHARS_PER_PAGE);
    if (fromBack) currentPage = totalPages - 1;

    renderPage(fullText, ragDocs, totalPages);
    switchView('view-pages');
}

// --- RENDERIZADO DE PÁGINAS ---
function renderPage(fullText, ragDocs, totalPages) {
    const start = currentPage * CHARS_PER_PAGE;
    const end = start + CHARS_PER_PAGE;
    const pageText = fullText.substring(start, end);

    const ragBox = document.getElementById('rag-info');
    if (currentPage === 0 && ragDocs.length > 0) {
        ragBox.innerHTML = "<strong>📎 Fragmentos Recuperados:</strong><br>" + ragDocs.map(d => `• ${d}`).join('<br>');
        ragBox.classList.remove('hidden');
    } else {
        ragBox.classList.add('hidden');
    }

    document.getElementById('page-text').innerText = pageText;
    document.getElementById('page-num').innerText = `${currentPage + 1} / ${totalPages}`;
    
    window.currentFullText = fullText;
    window.currentRagDocs = ragDocs;
    window.currentTotalPages = totalPages;
}

// --- NAVEGACIÓN ---
function nextPage() {
    if (currentPage < window.currentTotalPages - 1) {
        currentPage++;
        renderPage(window.currentFullText, window.currentRagDocs, window.currentTotalPages);
    } else {
        switchView('view-back');
    }
}

function prevPage() {
    if (currentPage > 0) {
        currentPage--;
        renderPage(window.currentFullText, window.currentRagDocs, window.currentTotalPages);
    } else {
        switchView('view-cover');
    }
}