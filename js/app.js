let robotDatabase = {};

// 页面加载时，立即从服务器获取最新的机器人数据
document.addEventListener('DOMContentLoaded', async () => {
    const resultsDiv = document.getElementById('results');
    const inputEl = document.getElementById('robotInput');
    try {
        const response = await fetch('data/robots.json?cache_bust=' + new Date().getTime());
        if (!response.ok) throw new Error('网络响应错误');
        
        const data = await response.json();
        robotDatabase = data.robots;
        
        resultsDiv.innerHTML = `<div class="robot-card">✅ 数据加载成功！<br>最后更新于: ${data.last_updated}<br>当前支持分析 ${Object.keys(robotDatabase).length} 款机器人。</div>`;
        inputEl.placeholder = '输入机器人型号, 如: spot';
        inputEl.disabled = false;

        console.log('机器人数据库已加载:', robotDatabase);

    } catch (error) {
        resultsDiv.innerHTML = `<div class="robot-card" style="color: red;">❌ 数据加载失败: ${error.message}</div>`;
        inputEl.placeholder = '数据加载失败';
        inputEl.disabled = true;
        console.error('加载机器人数据时出错:', error);
    }
});

function searchRobot() {
    const input = document.getElementById('robotInput').value.toLowerCase().trim();
    // ... 后面的 searchRobot, displayRobotInfo, createSankeyDiagram, drawSankey, clearSankeyDiagram 函数
    // 与上一个版本完全相同，直接复制粘贴即可。
    // 为了简洁此处省略，您可以从上一个版本的 js/app.js 完整复制这些函数。
    const resultsDiv = document.getElementById('results');
    if (!input) { resultsDiv.innerHTML = '<div class="robot-card">请输入机器人型号</div>'; return; }
    const robot = robotDatabase[input];
    if (robot) { displayRobotInfo(robot); createSankeyDiagram(robot); } else { resultsDiv.innerHTML = `<div class="robot-card"><h3>未找到 "${input}" 的信息</h3><p>目前支持的机器人：</p><ul>${Object.keys(robotDatabase).map(name => `<li>${name}</li>`).join('')}</ul></div>`; clearSankeyDiagram(); }
}
function displayRobotInfo(robot) { /* ... 和之前一样 ... */ const resultsDiv = document.getElementById('results'); let html = `<div class="robot-card"><h2>${robot.name}</h2><p><strong>制造商:</strong> ${robot.manufacturer}</p><p><strong>类型:</strong> ${robot.type}</p><h3 style="margin-top: 20px;">核心规格</h3><ul>${Object.entries(robot.specs).map(([key, value]) => `<li><strong>${key}:</strong> ${value}</li>`).join('')}</ul><h3 style="margin-top: 20px;">技术模块与供应链分析</h3>${Object.entries(robot.modules).map(([moduleName, data]) => `<div style="margin: 15px 0; padding: 15px; border-left: 4px solid #007bff; background: #f8f9fa; border-radius: 4px;"><h4>${moduleName}</h4><p><strong>关键组件:</strong> ${data.components.join('、 ')}</p><p><strong>主要供应商:</strong> ${data.suppliers.join('、 ')}</p></div>`).join('')}</div>`; resultsDiv.innerHTML = html; }
function createSankeyDiagram(robot) { /* ... 和之前一样 ... */ const container = document.getElementById('sankey-diagram'); container.innerHTML = ''; const nodes = []; const links = []; const nodeSet = new Set(); const addNode = (name, category) => { if (!nodeSet.has(name)) { nodeSet.add(name); nodes.push({ name, category }); } }; addNode(robot.name, 'robot'); Object.keys(robot.modules).forEach(moduleName => addNode(moduleName, 'module')); Object.values(robot.modules).forEach(data => data.suppliers.forEach(supplier => addNode(supplier, 'supplier'))); const findNodeIndex = (name) => nodes.findIndex(n => n.name === name); Object.entries(robot.modules).forEach(([moduleName, data]) => { links.push({ source: findNodeIndex(robot.name), target: findNodeIndex(moduleName), value: 10 }); data.suppliers.forEach(supplier => { links.push({ source: findNodeIndex(moduleName), target: findNodeIndex(supplier), value: 2 }); }); }); drawSankey(container, { nodes, links }); }
function drawSankey(container, data) { /* ... 和之前一样 ... */ if (!data.nodes.length || !data.links.length) return; const width = container.clientWidth; const height = container.clientHeight; const svg = d3.select(container).append("svg").attr("width", width).attr("height", height); const sankey = d3.sankey().nodeWidth(15).nodePadding(10).extent([[1, 5], [width - 1, height - 5]]); const {nodes, links} = sankey(data); const color = d3.scaleOrdinal().domain(['robot', 'module', 'supplier']).range(['#e41a1c', '#377eb8', '#4daf4a']); svg.append("g").selectAll("rect").data(nodes).join("rect").attr("x", d => d.x0).attr("y", d => d.y0).attr("height", d => d.y1 - d.y0).attr("width", d => d.x1 - d.x0).attr("fill", d => color(d.category)); const link = svg.append("g").attr("fill", "none").attr("stroke-opacity", 0.5).selectAll("g").data(links).join("g").style("mix-blend-mode", "multiply"); link.append("path").attr("d", d3.sankeyLinkHorizontal()).attr("stroke", d => color(d.source.category)).attr("stroke-width", d => Math.max(1, d.width)); svg.append("g").style("font", "12px sans-serif").selectAll("text").data(nodes).join("text").attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6).attr("y", d => (d.y1 + d.y0) / 2).attr("dy", "0.35em").attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end").text(d => d.name); }
function clearSankeyDiagram() { /* ... 和之前一样 ... */ document.getElementById('sankey-diagram').innerHTML = ''; }
document.getElementById('robotInput').addEventListener('keypress', function(e) { if (e.key === 'Enter') { searchRobot(); } });
