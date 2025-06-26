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
    let allLogs = {}; // Para armazenar os logs carregados e evitar recarregá-los

    // Função principal para carregar todos os dados iniciais
    async function loadInitialData() {
        try {
            // Carrega o arquivo de resultados da análise de IA
            const response = await fetch('./reports/relatorio_analise_modelos.jsonl');
            const text = await response.text();
            allReports = text.trim().split('\n').map(line => JSON.parse(line));
            
            populateFilters();
            displayResults();
        } catch (error) {
            resultsContainer.innerHTML = `<p style="color:red;">Erro ao carregar o arquivo de relatórios: ${error}</p>`;
            console.error(error);
        }
    }

    // Preenche os menus de filtro com base nos dados carregados
    function populateFilters() {
        const participantes = [...new Set(allReports.map(r => r.participante))].sort();
        const imagens = [...new Set(allReports.map(r => r.media_name))].sort();
        const categorias = [...new Set(allReports.map(r => r.categoria))].sort();
        const blocos = [...new Set(allReports.map(r => r.bloco))].sort();

        participantes.forEach(p => filterParticipante.add(new Option(p, p)));
        imagens.forEach(i => filterImagem.add(new Option(i, i)));
        categorias.forEach(c => filterCategoria.add(new Option(c, c)));
        blocos.forEach(b => filterBloco.add(new Option(b, b)));
    }

    // Filtra e exibe os resultados na página
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

        resultsContainer.innerHTML = ''; // Limpa os resultados anteriores
        resultsCount.textContent = `${filteredReports.length} resultado(s) encontrado(s).`;

        filteredReports.forEach(report => {
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
                        <div class="visualization-container" id="vis-container-${report.participante}-${report.media_name.split('.')[0]}">
                           <img src="./images/${report.media_name}" alt="${report.media_name}">
                        </div>
                    </div>
                </div>
            `;
            resultsContainer.appendChild(card);
            // Gera os gráficos para este card
            generateVisualizations(report);
        });
    }

    async function getFixationData(report) {
        const logFileName = `${String(report.bloco).padStart(2, '0')}_kh0${String(report.participante).padStart(2, '0')}_fixations.csv`;
        if (allLogs[logFileName]) {
            return allLogs[logFileName].filter(row => row.MEDIA_NAME === report.media_name);
        }

        try {
            const response = await fetch(`./eyetracker_logs/${logFileName}`);
            const csvText = await response.text();
            // Simples conversor de CSV para JSON
            const lines = csvText.trim().split('\n');
            const headers = lines.shift().split(',');
            constjsonData = lines.map(line => {
                const values = line.split(',');
                const obj = {};
                headers.forEach((header, i) => obj[header] = values[i]);
                return obj;
            });
            allLogs[logFileName] = jsonData;
            return jsonData.filter(row => row.MEDIA_NAME === report.media_name);
        } catch (error) {
            console.error(`Erro ao carregar log ${logFileName}:`, error);
            return [];
        }
    }

    // Gera os gráficos interativos
    async function generateVisualizations(report) {
        const fixations = await getFixationData(report);
        if (fixations.length === 0) return;

        const containerId = `vis-container-${report.participante}-${report.media_name.split('.')[0]}`;
        const container = document.getElementById(containerId);
        
        // Heatmap
        const heatmapContainer = document.createElement('div');
        heatmapContainer.className = 'heatmap-container';
        container.appendChild(heatmapContainer);
        const heatmapInstance = h337.create({ container: heatmapContainer, radius: 20 });
        const points = fixations.map(f => ({
            x: Math.round(f.FPOGX * container.clientWidth),
            y: Math.round(f.FPOGY * container.clientHeight),
            value: 1 // Todas as fixações têm o mesmo "peso"
        }));
        heatmapInstance.setData({ max: 5, data: points });

        // Scanpath
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;

        const radius = 8;
        const coords = fixations.map(f => ({
            x: f.FPOGX * canvas.width,
            y: f.FPOGY * canvas.height
        }));

        // Desenha as linhas
        ctx.beginPath();
        ctx.moveTo(coords[0].x, coords[0].y);
        for (let i = 1; i < coords.length; i++) {
            ctx.lineTo(coords[i].x, coords[i].y);
        }
        ctx.strokeStyle = 'rgba(66, 135, 245, 0.7)';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Desenha os círculos e números
        coords.forEach((c, i) => {
            ctx.beginPath();
            ctx.arc(c.x, c.y, radius, 0, 2 * Math.PI);
            if (i === 0) ctx.fillStyle = 'rgba(46, 204, 113, 0.9)'; // Verde
            else if (i === coords.length - 1) ctx.fillStyle = 'rgba(231, 76, 60, 0.9)'; // Vermelho
            else ctx.fillStyle = 'rgba(52, 152, 219, 0.9)'; // Azul
            ctx.fill();
            
            ctx.fillStyle = 'white';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(i + 1, c.x, c.y);
        });
    }
    
    // Adiciona os listeners para os filtros.
    [filterParticipante, filterImagem, filterCategoria, filterBloco].forEach(filter => {
        filter.addEventListener('change', displayResults);
    });
    resetBtn.addEventListener('click', () => {
        filterParticipante.value = 'all';
        filterImagem.value = 'all';
        filterCategoria.value = 'all';
        filterBloco.value = 'all';
        displayResults();
    });

    // Inicia a aplicação
    loadInitialData();
});