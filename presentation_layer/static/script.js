// --- ESTADO GLOBAL ---
let appData = null; 
let currentBook = null; 
let currentPage = 0;
const CHARS_PER_PAGE = 650; // Reduje un poco para dar espacio al título en negrita

// --- MOMENTO 1 -> 2: START ANALYSIS ---
async function startAnalysis() {
    const query = document.getElementById('userQuery').value;
    const btn = document.getElementById('startBtn');
    
    if (!query) return alert("Por favor ingresa una pregunta.");

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
        
        appData = data; 
        
        document.getElementById('books-container').classList.remove('hidden');
        
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

    const coverImg = document.getElementById('cover-img');
    const safeName = agentName.toLowerCase().replace(' ', '_');
    
    coverImg.src = `/static/images/bk_${safeName}_f.png`;
    coverImg.onerror = () => { console.log("Imagen portada no encontrada"); };

    const backImg = document.getElementById('back-img');
    backImg.src = `/static/images/bk_${safeName}_b.png`;

    const pagePaper = document.querySelector('.page-paper');
    pagePaper.style.backgroundImage = `url('/static/images/bk_${safeName}_p.png')`;

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
        // Obtenemos solo el texto puro, el título lo pondremos en renderPage
        fullText = appData.synthesis;
    } else {
        const log = appData.logs.find(l => l.agent === currentBook);
        if (log) {
            // Obtenemos solo el pensamiento puro (sin concatenar título aquí)
            fullText = log.thought.trim();
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

// --- RENDERIZADO DE PÁGINAS (Aquí está la magia de la Negrilla) ---
function renderPage(fullText, ragDocs, totalPages) {
    const start = currentPage * CHARS_PER_PAGE;
    const end = start + CHARS_PER_PAGE;
    
    // Obtenemos el fragmento de texto
    let rawPageText = fullText.substring(start, end);

    // Convertimos saltos de linea (\n) a HTML (<br>) para que se vean bien con innerHTML
    let htmlPageText = rawPageText.replace(/\n/g, "<br>");

    const pageElement = document.getElementById('page-text');
    const ragBox = document.getElementById('rag-info');
    
    // --- LÓGICA DE VISUALIZACIÓN ---
    
    if (currentPage === 0) {
        // 1. Mostrar Tweets (RAG)
        if (ragDocs.length > 0) {
            ragBox.innerHTML = "<strong>Tweets Recuperados:</strong><br>" + ragDocs.map(d => `• ${d}`).join('<br>');
            ragBox.classList.remove('hidden');
        } else {
            ragBox.classList.add('hidden');
        }

        // 2. Determinar Título
        let title = "Pensamiento Interno:";
        if (currentBook === "The Historian") title = "Síntesis del Archivero:";

        pageElement.innerHTML = `<strong style="font-size: 1.1em;">${title}</strong><br>${htmlPageText}`;
        
    } else {
        // Páginas siguientes: Solo texto, sin tweets ni título
        ragBox.classList.add('hidden');
        pageElement.innerHTML = htmlPageText;
    }

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