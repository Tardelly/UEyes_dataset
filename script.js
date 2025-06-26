
document.addEventListener('DOMContentLoaded', () => {
    // Referências aos elementos da página
    const filterParticipante = document.getElementById('filter-participante');
    const filterImagem = document.getElementById('filter-imagem');
    const filterCategoria = document.getElementById('filter-categoria');
    const filterBloco = document.getElementById('filter-bloco');
    const resultsContainer = document.getElementById('results-container');
    const resultsCount = document.getElementById('results-count');
    const resetBtn = document.getElementById('reset-filters');

    let allReports = [];
    let allLogsCache = {}; // Cache para evitar recarregar os mesmos logs

    // Função principal para carregar os dados
    async function loadInitialData() {
        try {
            const response = await fetch('./reports/relatorio_analise_modelos.jsonl');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const text = await response.text();
            allReports = text.trim().split('\n').map(line => JSON.parse(line));
            
            populateFilters();
            displayResults();
        } catch (error) {
            resultsContainer.innerHTML = `<p style="color:red; font-weight:bold;">Erro Crítico: Não foi possível carregar o arquivo de relatórios 'relatorio_analise_modelos.jsonl'. Verifique se o arquivo existe na pasta 'reports/' e se o caminho está correto.</p><p>Detalhe: ${error}</p>`;
            console.error("Erro ao carregar dados:", error);
        }
    }

    // Preenche os menus de filtro
    function populateFilters() {
        const createOptions = (element, values) => {
            [...new Set(values)].sort().forEach(value => element.add(new Option(value, value)));
        };
        createOptions(filterParticipante, allReports.map(r => r.participante));
        createOptions(filterImagem, allReports.map(r => r.media_name));
        createOptions(filterCategoria, allReports.map(r => r.categoria));
        createOptions(filterBloco, allReports.map(r => r.bloco));
    }

    // Exibe os resultados filtrados
    function displayResults() {
        const pVal = filterParticipante.value;
        const iVal = filterImagem.value;
        const cVal = filterCategoria.value;
        const bVal = filterBloco.value;

        const filteredReports = allReports.filter(r => 
            (pVal === 'all' || r.participante === pVal) &&
            (iVal === 'all' || r.media_name === iVal) &&
            (cVal === 'all' || r.categoria === cVal) &&
            (bVal === 'all' || r.bloco == bVal)
        );

        resultsContainer.innerHTML = ''; 
        resultsCount.textContent = `${filteredReports.length} resultado(s) encontrado(s).`;

        filteredReports.forEach(report => {
            const cardId = `card-${report.participante}-${report.media_name.replace('.', '_')}`;
            const card = document.createElement('div');
            card.className = 'report-card';
            card.innerHTML = `
                <div class="report-header">
                    <h3>${report.media_name}</h3>
                    <p>Participante: ${report.participante} | Categoria: ${report.categoria} | Bloco: ${report.bloco}</p>
                </div>
                <div class="report-content">
                    <div class="text-container">
                        <h4>Relatório do Modelo</h4>
                        <pre class="report-text">${report.Resposta}</pre>
                    </div>
                    <div class="visuals-container">
                        <h4>Visualizações Interativas</h4>
                        <div class="visualization-container" id="${cardId}">
                           <img src="./images/${report.media_name}" alt="${report.media_name}" onload="this.style.opacity=1" style="opacity:0; transition: opacity 0.5s;">
                        </div>
                    </div>
                </div>
            `;
            resultsContainer.appendChild(card);
            generateVisualizations(report, cardId);
        });
    }

    // Busca e processa o arquivo CSV de fixações
    async function getFixationData(report) {
        const logFileName = `${String(report.bloco).padStart(2, '0')}_kh0${String(report.participante).padStart(2, '0')}_fixations.csv`;
        if (allLogsCache[logFileName]) {
            return allLogsCache[logFileName].filter(row => row.MEDIA_NAME === report.media_name);
        }
        try {
            const response = await fetch(`./eyetracker_logs/${logFileName}`);
            if (!response.ok) return [];
            const csvText = await response.text();
            const lines = csvText.trim().split('\n');
            const headers = lines.shift().split(',').map(h => h.trim());
            const jsonData = lines.map(line => {
                const values = line.split(',');
                return headers.reduce((obj, header, i) => {
                    obj[header] = values[i] ? values[i].trim() : '';
                    return obj;
                }, {});
            });
            allLogsCache[logFileName] = jsonData;
            return jsonData.filter(row => row.MEDIA_NAME === report.media_name);
        } catch (error) {
            console.error(`Erro ao carregar log ${logFileName}:`, error);
            return [];
        }
    }

async function generateVisualizations(report, containerId) {
    const fixations = await getFixationData(report);
    if (fixations.length === 0) return;

    const container = document.getElementById(containerId);
    if (!container) return;

    // --- CRIAÇÃO DOS CONTROLES (CHECKBOXES) ---
    const controlsContainer = document.createElement('div');
    controlsContainer.className = 'layer-controls';
    controlsContainer.innerHTML = `
        <label><input type="checkbox" class="layer-toggle" data-layer="heatmap" checked> Heatmap</label>
        <label><input type="checkbox" class="layer-toggle" data-layer="scanpath" checked> Scanpath</label>
    `;
    const visualsContainer = container.closest('.visuals-container');
    visualsContainer.appendChild(controlsContainer);

    // --- CRIAÇÃO DO CANVAS ÚNICO PARA AMBOS OS GRÁFICOS ---
    const canvas = document.createElement('canvas');
    canvas.className = 'scanpath-canvas'; // Podemos reutilizar a classe CSS
    container.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    // --- FUNÇÃO CENTRAL DE REDESENHO ---
    // Esta função será chamada sempre que uma camada for ligada/desligada
    // ou quando a tela for redimensionada.
    const redrawAll = () => {
        if (container.clientWidth <= 0 || container.clientHeight <= 0) return;

        // Ajusta o tamanho do canvas
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;

        // Limpa tudo
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Verifica o estado dos checkboxes
        const showHeatmap = controlsContainer.querySelector('[data-layer="heatmap"]').checked;
        const showScanpath = controlsContainer.querySelector('[data-layer="scanpath"]').checked;

        // 1. Desenha o Heatmap (se estiver ligado)
        if (showHeatmap) {
            // A SimpleHeat desenha diretamente no canvas que fornecemos
            const heat = simpleheat(canvas); 
            
            // Converte os dados para o formato da SimpleHeat: [[x, y, value], ...]
            const heatData = fixations.map(f => {
                const x = parseFloat(f.FPOGX) * canvas.width;
                const y = parseFloat(f.FPOGY) * canvas.height;
                return [x, y, 1]; // [x, y, intensidade]
            }).filter(p => !isNaN(p[0]) && !isNaN(p[1]));

            heat.data(heatData); // Adiciona os dados
            heat.max(3); // Define o máximo (ajuste se quiser mais ou menos intenso)
            heat.radius(30, 20); // Raio do ponto de calor e raio do blur
            heat.draw(); // Desenha no canvas
        }

        // 2. Desenha o Scanpath (se estiver ligado)
        if (showScanpath) {
            const radius = 8;
            const coords = fixations.map(f => ({
                x: parseFloat(f.FPOGX) * canvas.width,
                y: parseFloat(f.FPOGY) * canvas.height
            }));
            
            if (coords.length === 0) return;

            // Desenha as linhas
            ctx.beginPath();
            ctx.moveTo(coords[0].x, coords[0].y);
            coords.slice(1).forEach(c => ctx.lineTo(c.x, c.y));
            ctx.strokeStyle = 'rgba(0, 0, 255, 0.8)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Desenha os círculos e números
            coords.forEach((c, i) => {
                ctx.beginPath();
                ctx.arc(c.x, c.y, radius, 0, 2 * Math.PI);
                if (i === 0) ctx.fillStyle = 'rgba(46, 204, 113, 1)';
                else if (i === coords.length - 1) ctx.fillStyle = 'rgba(231, 76, 60, 1)';
                else ctx.fillStyle = 'rgba(52, 152, 219, 1)';
                ctx.fill();
                
                ctx.fillStyle = 'white';
                ctx.font = 'bold 10px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(i + 1, c.x, c.y);
            });
        }
    };

    // --- LISTENERS DE EVENTOS ---
    // Redesenha tudo quando um checkbox muda
    controlsContainer.addEventListener('change', redrawAll);
    // Redesenha tudo quando o container muda de tamanho
    new ResizeObserver(redrawAll).observe(container);
    // Desenho inicial
    requestAnimationFrame(redrawAll);
}


    
    // Adiciona os listeners aos filtros
    
    [filterParticipante, filterImagem, filterCategoria, filterBloco].forEach(f => f.addEventListener('change', displayResults));
    resetBtn.addEventListener('click', () => {
        document.querySelectorAll('.filter-select').forEach(s => s.value = 'all');
        displayResults();
    });

    // Inicia a aplicação
    loadInitialData();
});