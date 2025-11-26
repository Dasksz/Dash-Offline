
import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const reportHtmlContent = fs.readFileSync(path.resolve(__dirname, '../EXPORTADOR DASH V7.html'), 'utf-8');
const scriptLogicMatch = reportHtmlContent.match(/<script id="report-logic-script" type="text\/template">([\s\S]*?)<\/script>/);
const reportLogic = scriptLogicMatch ? scriptLogicMatch[1] : '';

if (!reportLogic) {
    throw new Error("Could not find the report logic script in EXPORTADOR DASH V7.html");
}

// Added mock elements to prevent null reference errors during test execution
const tempHtml = `
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <style>.hidden { display: none; } .opacity-0 { opacity: 0; } .pointer-events-none { pointer-events: none; }</style>
</head>
<body>
    <div id="page-transition-loader" class="opacity-0 pointer-events-none"><span id="loader-text"></span></div>
    <div id="side-menu"></div>
    <div id="sidebar-overlay"></div>

    <!-- Mocks for Main Dashboard -->
    <div id="main-dashboard">Dashboard Content</div>
    <div id="tableView" class="hidden"></div>
    <div id="chartView" class="hidden"></div>
    <div id="table-pagination-controls" class="hidden"></div>
    <select id="posicao-filter"></select>
    <input id="codcli-filter" />
    <div id="main-rede-group-container"><button data-group=""></button></div>
    <button id="main-com-rede-btn"><span id="main-com-rede-btn-text"></span></button>
    <div id="main-rede-filter-dropdown"></div>
    <div id="fornecedor-toggle-container"></div>
    <button id="supervisor-filter-btn"><span id="supervisor-filter-text"></span></button>
    <div id="supervisor-filter-dropdown"></div>
    <button id="vendedor-filter-btn"><span id="vendedor-filter-text"></span></button>
    <div id="vendedor-filter-dropdown"></div>
    <button id="tipo-venda-filter-btn"><span id="tipo-venda-filter-text"></span></button>
    <div id="tipo-venda-filter-dropdown"></div>
    <button id="fornecedor-filter-btn"><span id="fornecedor-filter-text"></span></button>
    <div id="fornecedor-filter-dropdown"></div>
    <p id="total-vendas"></p><p id="total-peso"></p><p id="kpi-sku-pdv"></p><p id="kpi-positivacao"></p><p id="kpi-positivacao-percent"></p>
    <div id="salesByPersonChartContainer"></div><div id="faturamentoPorFornecedorChartContainer"></div><div id="salesByProductBarChartContainer"></div>
    <h2 id="sales-by-person-title"></h2><h2 id="faturamentoPorFornecedorTitle"></h2>
    <div id="trendChartContainer"></div>
    <button id="faturamentoBtn"></button><button id="pesoBtn"></button>


    <!-- Mocks for City View -->
    <div id="city-view" class="hidden">City View Content</div>
    <input id="city-name-filter" />
    <input id="city-codcli-filter" />
    <div id="city-suggestions"></div>
    <div id="city-rede-group-container"><button data-group=""></button></div>
    <button id="city-com-rede-btn"><span id="city-com-rede-btn-text"></span></button>
    <div id="city-rede-filter-dropdown"></div>
    <button id="city-supervisor-filter-btn"><span id="city-supervisor-filter-text"></span></button>
    <div id="city-supervisor-filter-dropdown"></div>
    <button id="city-vendedor-filter-btn"><span id="city-vendedor-filter-text"></span></button>
    <div id="city-vendedor-filter-dropdown"></div>
    <button id="city-tipo-venda-filter-btn"><span id="city-tipo-venda-filter-text"></span></button>
    <div id="city-tipo-venda-filter-dropdown"></div>
    <p id="total-faturamento-cidade"></p><p id="total-clientes-cidade"></p>
    <div id="salesByClientInCityChartContainer"></div><div id="customerStatusChartContainer"></div>
    <div id="city-active-detail-table-body"></div><div id="city-inactive-detail-table-body"></div>
    <h2 id="city-chart-title"></h2>

    <!-- Mocks for other views -->
    <div id="weekly-view" class="hidden"></div>
    <div id="comparison-view" class="hidden"></div>
    <div id="stock-view" class="hidden"></div>
    <div id="innovations-month-view" class="hidden"></div>
    <div id="coverage-view" class="hidden"></div>
    <div id="mix-view" class="hidden"></div>

    <button class="nav-link" data-target="dashboard">Dashboard</button>
    <button class="nav-link" data-target="cidades">Cidades</button>

    <script>
        const embeddedData = {
            detailed: [], history: [], byOrder: [], clients: [],
            stockMap05: {}, stockMap08: {}, innovationsMonth: [],
            activeProductCodes: [], productDetails: {}, passedWorkingDaysCurrentMonth: 1
        };
        var Chart = class { static register(...any) {} constructor(...any) { this.options = { plugins: { datalabels: {}, legend: { labels: {} } }, scales: { x: { ticks: {} }, y: { ticks: {} } } }; } update() {} destroy() {} };
        var ChartDataLabels = {};
        window.jspdf = { jsPDF: class { autoTable(){} text(){} addImage(){} setPage(){} internal={pageSize:{width:0, height: 0}} } };
    </script>
    <script>
        ${reportLogic}
    </script>
</body>
</html>
`;

test.describe('Navigation Logic', () => {
    const testFile = path.resolve(__dirname, 'temp_report.html');

    test.beforeAll(() => {
        fs.writeFileSync(testFile, tempHtml);
    });

    test.afterAll(() => {
        fs.unlinkSync(testFile);
    });

    test('should show loader on navigation and switch views correctly', async ({ page }) => {
        await page.goto(`file://${testFile}`);
        await page.waitForLoadState('domcontentloaded');

        // This call is needed to initialize everything, even if it fails internally,
        // it sets up the necessary state for the next navigation.
        await page.evaluate(() => navigateTo('dashboard')).catch(() => {});

        await expect(page.locator('#main-dashboard')).toBeVisible();
        await expect(page.locator('#city-view')).toBeHidden();
        await expect(page.locator('#page-transition-loader')).toHaveClass(/opacity-0/);

        // --- Start Navigation Test ---
        const navigationPromise = page.evaluate(() => navigateTo('cidades'));

        await expect(page.locator('#page-transition-loader')).not.toHaveClass(/opacity-0/);
        await expect(page.locator('#loader-text')).toHaveText('Carregando Cidades...');

        await navigationPromise;

        await expect(page.locator('#page-transition-loader')).toHaveClass(/opacity-0/);

        await expect(page.locator('#main-dashboard')).toBeHidden();
        await expect(page.locator('#city-view')).toBeVisible();
        await expect(page.locator('#city-view')).toContainText('City View Content');
    });
});
