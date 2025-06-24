// ... (文件顶部的 let robotDatabase = {}; 和 DOMContentLoaded 事件监听器保持不变)
let robotDatabase = {};

document.addEventListener('DOMContentLoaded', async () => {
    const statusDiv = document.getElementById('status');
    const inputEl = document.getElementById('robotInput');
    try {
        const response = await fetch('data/robots.json?cache_bust=' + new Date().getTime());
        if (!response.ok) throw new Error(`网络响应错误: ${response.status}`);
        const data = await response.json();
        robotDatabase = data.robots;
        
        statusDiv.innerHTML = `✅ 数据同步成功！最后更新于: ${data.last_updated}<br>当前收录 ${Object.keys(robotDatabase).length} 款机器人。在下方搜索框中试试: ${Object.keys(robotDatabase).join(', ')}`;
        inputEl.placeholder = '输入机器人名称 (e.g., spot)';
        inputEl.disabled = false;

    } catch (error) {
        statusDiv.innerHTML = `❌ 数据同步失败: ${error.message}`;
        inputEl.placeholder = '数据加载失败';
        inputEl.disabled = true;
    }
});

function searchRobot() {
    const input = document.getElementById('robotInput').value.toLowerCase().trim();
    const resultsContainer = document.getElementById('resultsContainer');
    const statusDiv = document.getElementById('status');
    
    if (!input) {
        statusDiv.style.display = 'block';
        statusDiv.textContent = '请输入一个机器人名称。';
        resultsContainer.classList.remove('visible');
        return;
    }
    
    const robot = robotDatabase[input];
    
    if (robot) {
        statusDiv.style.display = 'none';
        displayRobotInfo(robot);
        createSankeyDiagram(robot);
        resultsContainer.classList.add('visible');
    } else {
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = `<h3>未找到关于 "${input}" 的信息</h3><p>我们收录的机器人有: ${Object.keys(robotDatabase).join(', ')}</p><p>想添加新的？请在GitHub仓库编辑 'robots_to_scrape.txt' 文件！</p>`;
        resultsContainer.classList.remove('visible');
    }
}

function displayRobotInfo(robot) {
    const infoDiv = document.getElementById('robotInfo');
    
    const specsHTML = Object.entries(robot.specs).map(([key, value]) => `
        <div class="spec-item">
            <strong>${key}</strong>
            <span>${value !== 'N/A' ? value : '---'}</span>
        </div>
    `).join('');

    const modulesHTML = Object.entries(robot.modules).map(([moduleName, data]) => `
        <div class="module-item">
            <h4>${moduleName}</h4>
            <p><strong>关键组件:</strong> ${data.components.join('、 ')}</p>
            <p><strong>主要供应商:</strong> ${data.suppliers.join('、 ')}</p>
        </div>
    `).join('');

    let html = `
        <h2>${robot.name}</h2>
        <p><strong>制造商:</strong> ${robot.manufacturer} | <strong>类型:</strong> ${robot.type}</p>
        <div class="spec-grid">${specsHTML}</div>
        <div class="module-section">
            <h3>核心模块解析</h3>
            ${modulesHTML}
        </div>
    `;
    infoDiv.innerHTML = html;
}

// ... (createSankeyDiagram 和 drawSankey 函数保持不变，直接从旧文件复制)
// 注意：为了让Sankey图的文字在暗色背景下可见，在 drawSankey 函数的最后添加一行：
// .style('fill', 'var(--text-muted)'); 
// 例如：
function drawSankey(container, data) {
    // ... (原有的绘图代码) ...
    svg.append("g").style("font", "12px sans-serif")
      .selectAll("text").data(nodes).join("text")
        .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
        .attr("y", d => (d.y1 + d.y0) / 2).attr("dy", "0.35em")
        .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
        .text(d => d.name)
        .style('fill', 'var(--text-muted)'); // <--- 添加这一行
}
//... 
//... The rest of the functions (createSankey, drawSankey, clearSankey) remain the same.
//... You can copy them from your previous version.

function createSankeyDiagram(robot) { /* ... 和之前一样 ... */ const container = document.getElementById('sankey-diagram'); container.innerHTML = ''; const nodes = []; const links = []; const nodeSet = new Set(); const addNode = (name, category) => { if (!nodeSet.has(name)) { nodeSet.add(name); nodes.push({ name, category }); } }; addNode(robot.name, 'robot'); Object.keys(robot.modules).forEach(moduleName => addNode(moduleName, 'module')); Object.values(robot.modules).forEach(data => data.suppliers.forEach(supplier => addNode(supplier, 'supplier'))); const findNodeIndex = (name) => nodes.findIndex(n => n.name === name); Object.entries(robot.modules).forEach(([moduleName, data]) => { links.push({ source: findNodeIndex(robot.name), target: findNodeIndex(moduleName), value: 10 }); data.suppliers.forEach(supplier => { links.push({ source: findNodeIndex(moduleName), target: findNodeIndex(supplier), value: 2 }); }); }); drawSankey(container, { nodes, links }); }
document.getElementById('robotInput').addEventListener('keypress', function(e) { if (e.key === 'Enter') { searchRobot(); } });
