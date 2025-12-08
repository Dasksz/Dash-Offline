import re

file_path = 'EXPORTADOR DASH V7.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the start and end of the function to be replaced
start_marker = "function updateGoalsSvView() {"
end_marker = "}, () => currentRenderId !== goalsSvRenderId);"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx != -1 and end_idx != -1:
    # We need to capture the full function body up to the closing brace of the runAsyncChunked callback wrapper
    # But wait, updateGoalsSvView ends with }, () => currentRenderId !== goalsSvRenderId);
    # then a closing brace for the function itself.

    # Let's find the closing brace of the function
    func_end_idx = content.find("}", end_idx + len(end_marker))

    if func_end_idx != -1:
        new_function = r"""function updateGoalsSvView() {
            goalsSvRenderId++;
            const currentRenderId = goalsSvRenderId;

            if (quarterMonths.length === 0) identifyQuarterMonths();
            const filteredClients = getGoalsSvFilteredData();

            // Define Column Blocks (Metrics Config)
            const svColumns = [
                { id: 'total_elma', label: 'TOTAL ELMA', type: 'standard', isAgg: true, colorClass: 'text-teal-400', components: ['707', '708', '752'] },
                { id: '707', label: 'EXTRUSADOS', type: 'standard', supplier: '707', brand: null, colorClass: 'text-slate-300' },
                { id: '708', label: 'NÃO EXTRUSADOS', type: 'standard', supplier: '708', brand: null, colorClass: 'text-slate-300' },
                { id: '752', label: 'TORCIDA', type: 'standard', supplier: '752', brand: null, colorClass: 'text-slate-300' },
                { id: 'tonelada_elma', label: 'TONELADA ELMA', type: 'tonnage', isAgg: true, colorClass: 'text-orange-400', components: ['707', '708', '752'] },
                { id: 'mix_salty', label: 'MIX SALTY', type: 'mix', isAgg: true, colorClass: 'text-teal-400', components: [] },
                { id: 'total_foods', label: 'TOTAL FOODS', type: 'standard', isAgg: true, colorClass: 'text-yellow-400', components: ['1119_TODDYNHO', '1119_TODDY', '1119_QUAKER_KEROCOCO'] },
                { id: '1119_TODDYNHO', label: 'TODDYNHO', type: 'standard', supplier: '1119', brand: 'TODDYNHO', colorClass: 'text-slate-300' },
                { id: '1119_TODDY', label: 'TODDY', type: 'standard', supplier: '1119', brand: 'TODDY', colorClass: 'text-slate-300' },
                { id: '1119_QUAKER_KEROCOCO', label: 'QUAKER / KEROCOCO', type: 'standard', supplier: '1119', brand: 'QUAKER_KEROCOCO', colorClass: 'text-slate-300' },
                { id: 'tonelada_foods', label: 'TONELADA FOODS', type: 'tonnage', isAgg: true, colorClass: 'text-orange-400', components: ['1119_TODDYNHO', '1119_TODDY', '1119_QUAKER_KEROCOCO'] },
                { id: 'mix_foods', label: 'MIX FOODS', type: 'mix', isAgg: true, colorClass: 'text-yellow-400', components: [] },
                { id: 'geral', label: 'GERAL', type: 'geral', isAgg: true, colorClass: 'text-white', components: ['total_elma', 'total_foods'] },
                { id: 'pedev', label: 'AUDITORIA PEDEV', type: 'pedev', isAgg: true, colorClass: 'text-pink-400', components: ['total_elma'] }
            ];

            const baseCategories = svColumns.filter(c => c.type === 'standard' && !c.isAgg);
            const mainTable = document.getElementById('goals-sv-main-table');
            if (mainTable) mainTable.innerHTML = '<tbody><tr><td class="text-center p-8"><svg class="animate-spin h-8 w-8 text-teal-500 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg></td></tr></tbody>';

            // Ensure Global Totals are cached (Sync operation, but fast enough for initialization)
            baseCategories.forEach(cat => {
                const cacheKey = cat.supplier + (cat.brand ? `_${cat.brand}` : '');
                if (!globalGoalsTotalsCache[cacheKey]) calculateDistributedGoals([], cat.supplier, cat.brand, 0, 0);
            });

            // Prepare Aggregation Structures
            const sellerMap = new Map();
            const initSeller = (sellerName) => {
                if (!sellerMap.has(sellerName)) {
                    let sellerCode = optimizedData.rcaCodeByName.get(sellerName) || '';
                    let supervisorName = 'N/A';
                    if (sellerCode) {
                        for (const [sup, rcas] of optimizedData.rcasBySupervisor) {
                            if (rcas.includes(sellerCode)) { supervisorName = sup; break; }
                        }
                    }
                    sellerMap.set(sellerName, { name: sellerName, code: sellerCode, supervisor: supervisorName, data: {}, metaPosTotal: 0, elmaPos: 0, foodsPos: 0 });
                }
                return sellerMap.get(sellerName);
            };

            const currentDate = lastSaleDate;
            const prevMonthDate = new Date(Date.UTC(currentDate.getUTCFullYear(), currentDate.getUTCMonth() - 1, 1));
            const prevMonthIndex = prevMonthDate.getUTCMonth();
            const prevMonthYear = prevMonthDate.getUTCFullYear();

            // Optimization: Normalize functions outside loop
            const norm = (str) => str ? str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase() : '';

            // ASYNC LOOP
            runAsyncChunked(filteredClients, (client) => {
                const codCli = client['Código'];
                const clientHistoryIds = optimizedData.indices.history.byClient.get(codCli);

                let sellerName = 'N/A';
                const rcaCode = client.rcas[0];
                if (rcaCode) sellerName = optimizedData.rcaNameByCode.get(rcaCode) || rcaCode;
                const sellerObj = initSeller(sellerName);

                // Initialize client totals for each category
                const clientCatTotals = {};
                baseCategories.forEach(c => clientCatTotals[c.id] = { fat: 0, vol: 0, pos: 0, prevFat: 0, monthly: {} });

                // Single Pass over History for this Client
                if (clientHistoryIds) {
                    clientHistoryIds.forEach(id => {
                        const sale = optimizedData.historyById.get(id);
                        const isRev = (sale.TIPOVENDA === '1' || sale.TIPOVENDA === '9');
                        if (!isRev) return;

                        const codFor = String(sale.CODFOR);
                        let matchedCats = [];

                        // Determine which categories this sale belongs to
                        if (codFor === '707') matchedCats.push('707');
                        else if (codFor === '708') matchedCats.push('708');
                        else if (codFor === '752') matchedCats.push('752');
                        else if (codFor === '1119') {
                            const desc = norm(sale.DESCRICAO || '');
                            if (desc.includes('TODDYNHO')) matchedCats.push('1119_TODDYNHO');
                            else if (desc.includes('TODDY')) matchedCats.push('1119_TODDY');
                            else if (desc.includes('QUAKER') || desc.includes('KEROCOCO')) matchedCats.push('1119_QUAKER_KEROCOCO');
                        }

                        if (matchedCats.length > 0) {
                            const d = parseDate(sale.DTPED);
                            const isPrev = d && d.getUTCMonth() === prevMonthIndex && d.getUTCFullYear() === prevMonthYear;
                            const monthKey = d ? `${d.getUTCFullYear()}-${d.getUTCMonth()}` : null;

                            matchedCats.forEach(catId => {
                                const t = clientCatTotals[catId];
                                t.fat += sale.VLVENDA;
                                t.vol += sale.TOTPESOLIQ;
                                if (isPrev) t.prevFat += sale.VLVENDA;
                                if (monthKey) t.monthly[monthKey] = (t.monthly[monthKey] || 0) + sale.VLVENDA;
                            });
                        }
                    });
                }

                // Aggregate to Seller
                baseCategories.forEach(cat => {
                    const t = clientCatTotals[cat.id];
                    if (!sellerObj.data[cat.id]) sellerObj.data[cat.id] = { metaFat: 0, metaVol: 0, metaPos: 0, avgVol: 0, avgFat: 0, monthlyValues: {} };
                    const sData = sellerObj.data[cat.id];

                    const avgFat = t.fat / QUARTERLY_DIVISOR;
                    const avgVol = (t.vol / 1000) / QUARTERLY_DIVISOR;
                    const metaPos = t.fat > 1 ? 1 : 0;

                    // Fetch Stored Goal
                    let metaFat = 0; let metaVol = 0;
                    if (globalClientGoals.has(codCli)) {
                        const cacheKey = cat.supplier + (cat.brand ? `_${cat.brand}` : '');
                        const cGoals = globalClientGoals.get(codCli);
                        if (cGoals.has(cacheKey)) { const g = cGoals.get(cacheKey); metaFat = g.fat; metaVol = g.vol; }
                    }

                    sData.metaFat += metaFat;
                    sData.metaVol += metaVol;
                    sData.metaPos += metaPos;
                    sData.avgVol += avgVol;
                    sData.avgFat += avgFat;

                    // Monthly Breakdown
                    quarterMonths.forEach(m => {
                        if (!sData.monthlyValues[m.key]) sData.monthlyValues[m.key] = 0;
                        sData.monthlyValues[m.key] += (t.monthly[m.key] || 0);
                    });
                });

                // Calculate Aggregate Positivation for Client (Unique Client Count)
                let clientElmaFat = (clientCatTotals['707']?.fat || 0) + (clientCatTotals['708']?.fat || 0) + (clientCatTotals['752']?.fat || 0);
                if (clientElmaFat > 1) sellerObj.elmaPos++;

                let clientFoodsFat = (clientCatTotals['1119_TODDYNHO']?.fat || 0) + (clientCatTotals['1119_TODDY']?.fat || 0) + (clientCatTotals['1119_QUAKER_KEROCOCO']?.fat || 0);
                if (clientFoodsFat > 1) sellerObj.foodsPos++;

            }, () => {
                if (currentRenderId !== goalsSvRenderId) return;

                // --- FINALIZE AGGREGATION & RENDER ---

                // 1. Calculate Aggregates (Mix, Geral, etc.)
                sellerMap.forEach(sellerObj => {
                    // Override Meta Pos with Global Goals if set
                    if (globalSellerGoals[sellerObj.name]) {
                        Object.keys(sellerObj.data).forEach(catId => {
                            let lookupKey = catId;
                            // Match keys used in globalSellerGoals (distributePositivacao)
                            // The keys there are: '707', '708', '752', '1119_TODDYNHO', '1119_TODDY', '1119_QUAKER_KEROCOCO'
                            // AND aggregated keys: 'ELMA_ALL', 'FOODS_ALL'

                            // For base categories, direct match
                            // For aggregated columns in the View (total_elma, total_foods), we map them

                            if (globalSellerGoals[sellerObj.name][catId]) {
                                sellerObj.data[catId].metaPos = globalSellerGoals[sellerObj.name][catId].pos;
                            }
                        });

                        // Handle Aggregated Columns explicitly if they are not in sellerObj.data yet or need override
                        // Note: Aggregates like 'total_elma' are computed below.
                        // We should override AFTER computation or inject the value into a temp property to use during aggregation.
                        // Actually, 'distributePositivacao' sets goals for 'ELMA_ALL' and 'FOODS_ALL'.
                        // We should use those to override the SUM or COUNT logic for the Total Columns.
                    }

                    // Component Aggregates
                    svColumns.filter(c => c.isAgg && c.type !== 'mix' && c.type !== 'geral' && c.type !== 'pedev').forEach(aggCol => {
                        let sumFat = 0, sumVol = 0, sumPos = 0, sumAvgVol = 0, sumAvgFat = 0;
                        const monthlySum = {}; quarterMonths.forEach(m => monthlySum[m.key] = 0);
                        aggCol.components.forEach(compId => {
                            if (sellerObj.data[compId]) {
                                sumFat += sellerObj.data[compId].metaFat; sumVol += sellerObj.data[compId].metaVol;
                                sumPos += sellerObj.data[compId].metaPos; sumAvgVol += sellerObj.data[compId].avgVol;
                                sumAvgFat += sellerObj.data[compId].avgFat || 0;
                                quarterMonths.forEach(m => monthlySum[m.key] += (sellerObj.data[compId].monthlyValues[m.key] || 0));
                            }
                        });

                        // Use calculated unique client count for Total Elma/Foods DEFAULT
                        if (aggCol.id === 'total_elma') sumPos = sellerObj.elmaPos || 0;
                        else if (aggCol.id === 'total_foods') sumPos = sellerObj.foodsPos || 0;

                        // OVERRIDE Aggregated Positivation if manually set
                        if (globalSellerGoals[sellerObj.name]) {
                            let lookupKey = null;
                            if (aggCol.id === 'total_elma') lookupKey = 'ELMA_ALL';
                            else if (aggCol.id === 'total_foods') lookupKey = 'FOODS_ALL';

                            if (lookupKey && globalSellerGoals[sellerObj.name][lookupKey]) {
                                sumPos = globalSellerGoals[sellerObj.name][lookupKey].pos;
                            }
                        }

                        sellerObj.data[aggCol.id] = { metaFat: sumFat, metaVol: sumVol, metaPos: sumPos, avgVol: sumAvgVol, avgFat: sumAvgFat, monthlyValues: monthlySum };
                    });

                    // Mix Metrics
                    const historyIds = optimizedData.indices.history.byRca.get(sellerObj.name) || [];
                    let activeClientsCount = 0;

                    // Active Clients Count (Unique for this seller)
                    // If ELMA_ALL Pos or FOODS_ALL Pos is set manually, does it affect "Active Clients"?
                    // Usually "Meta Pos" for Geral is the sum of Unique Active Clients.
                    // If we override sub-goals, the Total Active Clients for the seller might be targetted too?
                    // Currently 'distributePositivacao' distributes to specific categories.
                    // For the 'Geral' column, we usually just count unique clients who bought anything > 1.
                    // Let's keep the Natural Count for Geral Meta Pos unless we want a specific 'GERAL' override (not requested).

                    const sellerClients = filteredClients.filter(c => {
                        const code = c.rcas[0];
                        const name = optimizedData.rcaNameByCode.get(code) || code;
                        return name === sellerObj.name;
                    });
                    sellerClients.forEach(c => {
                        const hIds = optimizedData.indices.history.byClient.get(c['Código']);
                        let totalFat = 0;
                        if(hIds) { for (const id of hIds) totalFat += optimizedData.historyById.get(id).VLVENDA; }
                        if (totalFat > 1) activeClientsCount++;
                    });

                    // Mix Calc
                    const monthlyData = new Map();
                    historyIds.forEach(id => {
                        const sale = optimizedData.historyById.get(id);
                        const d = parseDate(sale.DTPED);
                        if (!d) return;
                        const mKey = `${d.getUTCFullYear()}-${d.getUTCMonth()}`;
                        if (!monthlyData.has(mKey)) monthlyData.set(mKey, new Map());
                        const cMap = monthlyData.get(mKey);
                        if (!cMap.has(sale.CODCLI)) cMap.set(sale.CODCLI, { salty: new Set(), foods: new Set() });
                        const cData = cMap.get(sale.CODCLI);
                        if (sale.VLVENDA > 1) {
                            const desc = norm(sale.DESCRICAO);
                            MIX_SALTY_CATEGORIES.forEach(cat => { if (desc.includes(cat)) cData.salty.add(cat); });
                            MIX_FOODS_CATEGORIES.forEach(cat => { if (desc.includes(cat)) cData.foods.add(cat); });
                        }
                    });
                    let sumSalty = 0; let sumFoods = 0;
                    const months = Array.from(monthlyData.keys()).sort().slice(-3);
                    const divisor = months.length > 0 ? months.length : 1;
                    months.forEach(m => {
                        const cMap = monthlyData.get(m);
                        let mSalty = 0; let mFoods = 0;
                        cMap.forEach(d => {
                            if (d.salty.size >= MIX_SALTY_CATEGORIES.length) mSalty++;
                            if (d.foods.size >= MIX_FOODS_CATEGORIES.length) mFoods++;
                        });
                        sumSalty += mSalty; sumFoods += mFoods;
                    });

                    let mixSaltyMeta = Math.round(activeClientsCount * 0.60);
                    let mixFoodsMeta = Math.round(activeClientsCount * 0.30);
                    if (sellerObj.code === '1001') { mixSaltyMeta = 0; mixFoodsMeta = 0; }

                    sellerObj.data['mix_salty'] = { avgMix: sumSalty / divisor, metaMix: mixSaltyMeta };
                    sellerObj.data['mix_foods'] = { avgMix: sumFoods / divisor, metaMix: mixFoodsMeta };

                    // Geral & Pedev
                    const totalElma = sellerObj.data['total_elma'];
                    const totalFoods = sellerObj.data['total_foods'];

                    // Logic for GERAL Meta Pos:
                    // If we have manual overrides, simply summing them might double count if same client is targetted in both.
                    // However, we don't have a "Geral Override".
                    // Let's use the Natural Active Client count as the base.

                    sellerObj.data['geral'] = {
                        avgFat: (totalElma.avgFat || 0) + (totalFoods.avgFat || 0),
                        metaFat: totalElma.metaFat + totalFoods.metaFat,
                        metaVol: totalElma.metaVol + totalFoods.metaVol,
                        metaPos: activeClientsCount
                    };

                    // Pedev is 90% of Total Elma Pos (which might be overridden)
                    sellerObj.data['pedev'] = { metaPos: Math.round(totalElma.metaPos * 0.9) };
                });

                // Group Supervisors
                const supervisorGroups = new Map();
                sellerMap.forEach(seller => {
                    const supName = seller.supervisor;
                    if (!supervisorGroups.has(supName)) supervisorGroups.set(supName, { name: supName, id: supName.replace(/[^a-zA-Z0-9]/g, '_'), code: optimizedData.supervisorCodeByName.get(supName) || '', sellers: [], totals: {} });
                    supervisorGroups.get(supName).sellers.push(seller);
                });

                // Aggregate Totals
                supervisorGroups.forEach(group => {
                    svColumns.forEach(col => {
                        if (!group.totals[col.id]) group.totals[col.id] = { metaFat: 0, metaVol: 0, metaPos: 0, avgVol: 0, avgMix: 0, metaMix: 0, avgFat: 0, monthlyValues: {} };
                        quarterMonths.forEach(m => group.totals[col.id].monthlyValues[m.key] = 0);
                        group.sellers.forEach(seller => {
                            if (seller.data[col.id]) {
                                const s = seller.data[col.id]; const t = group.totals[col.id];
                                t.metaFat += s.metaFat || 0; t.metaVol += s.metaVol || 0; t.metaPos += s.metaPos || 0;
                                t.avgVol += s.avgVol || 0; t.avgMix += s.avgMix || 0; t.metaMix += s.metaMix || 0; t.avgFat += s.avgFat || 0;
                                if (s.monthlyValues) quarterMonths.forEach(m => t.monthlyValues[m.key] += s.monthlyValues[m.key]);
                            }
                        });
                    });
                });

                const sortedSupervisors = Array.from(supervisorGroups.values()).sort((a, b) => (b.totals['total_elma']?.metaFat || 0) - (a.totals['total_elma']?.metaFat || 0));
                currentGoalsSvData = sortedSupervisors;

                // Render HTML
                if (!mainTable) return;
                const monthsCount = quarterMonths.length;
                let headerHTML = `<thead class="text-[10px] uppercase sticky top-0 z-20 bg-[#0f172a] text-slate-400"><tr><th rowspan="3" class="px-2 py-2 text-center w-16 border-r border-b border-slate-700">CÓD</th><th rowspan="3" class="px-3 py-2 text-left w-48 border-r border-b border-slate-700">VENDEDOR</th>`;
                svColumns.forEach(col => {
                    let colspan = 2;
                    if (col.type === 'standard') colspan = monthsCount + 1 + 4;
                    if (col.type === 'tonnage') colspan = 3; if (col.type === 'mix') colspan = 3; if (col.type === 'geral') colspan = 4;
                    headerHTML += `<th colspan="${colspan}" class="px-2 py-2 text-center font-bold border-r border-b border-slate-700 ${col.colorClass}">${col.label}</th>`;
                });
                headerHTML += `</tr><tr>`;
                svColumns.forEach(col => {
                    if (col.type === 'standard') headerHTML += `<th colspan="${monthsCount + 1}" class="px-1 py-1 text-center border-r border-slate-700/50 bg-slate-800/50">HISTÓRICO FAT.</th><th colspan="2" class="px-1 py-1 text-center border-r border-slate-700/50 bg-slate-800/50">FATURAMENTO</th><th colspan="2" class="px-1 py-1 text-center border-r border-slate-700 bg-slate-800/50">POSITIVAÇÃO</th>`;
                    else if (col.type === 'tonnage') headerHTML += `<th class="px-1 py-1 text-right border-r border-slate-700/50 bg-slate-800/50">MÉDIA TRIM.</th><th colspan="2" class="px-1 py-1 text-center border-r border-slate-700 bg-slate-800/50">META TON</th>`;
                    else if (col.type === 'mix') headerHTML += `<th class="px-1 py-1 text-right border-r border-slate-700/50 bg-slate-800/50">MÉDIA TRIM.</th><th colspan="2" class="px-1 py-1 text-center border-r border-slate-700 bg-slate-800/50">META MIX</th>`;
                    else if (col.type === 'geral') headerHTML += `<th colspan="2" class="px-1 py-1 text-center border-r border-slate-700/50 bg-slate-800/50">FATURAMENTO</th><th class="px-1 py-1 text-center border-r border-slate-700/50 bg-slate-800/50">TONELADA</th><th class="px-1 py-1 text-center border-r border-slate-700 bg-slate-800/50">POSITIVAÇÃO</th>`;
                    else if (col.type === 'pedev') headerHTML += `<th class="px-1 py-1 text-center border-r border-slate-700/50 bg-slate-800/50">META</th>`;
                });
                headerHTML += `</tr><tr>`;
                const gearIcon = `<svg class="w-3 h-3 mx-auto text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`;
                svColumns.forEach(col => {
                    if (col.type === 'standard') {
                        quarterMonths.forEach(m => headerHTML += `<th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal w-12">${m.label}</th>`);
                        headerHTML += `<th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Média</th><th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Meta</th><th class="px-1 py-1 text-center border-r border-b border-slate-700 text-slate-500 font-normal">${gearIcon}</th><th class="px-1 py-1 text-center border-r border-b border-slate-700 text-slate-500 font-normal">Meta</th><th class="px-1 py-1 text-center border-r border-b border-slate-700 text-slate-500 font-normal">${gearIcon}</th>`;
                    } else if (col.type === 'tonnage') headerHTML += `<th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Volume</th><th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Volume</th><th class="px-1 py-1 text-center border-r border-b border-slate-700 text-slate-500 font-normal">${gearIcon}</th>`;
                    else if (col.type === 'mix') headerHTML += `<th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Qtd</th><th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Meta</th><th class="px-1 py-1 text-center border-r border-b border-slate-700 text-slate-500 font-normal">${gearIcon}</th>`;
                    else if (col.type === 'geral') headerHTML += `<th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Média Trim.</th><th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Meta</th><th class="px-1 py-1 text-right border-r border-b border-slate-700 text-slate-500 font-normal">Meta</th><th class="px-1 py-1 text-center border-r border-b border-slate-700 text-slate-500 font-normal">Meta</th>`;
                    else if (col.type === 'pedev') headerHTML += `<th class="px-1 py-1 text-center border-r border-b border-slate-700 text-slate-500 font-normal">${gearIcon}</th>`;
                });
                headerHTML += `</tr></thead>`;

                let bodyHTML = `<tbody class="divide-y divide-slate-800 bg-[#151c36]">`;
                // Grand Totals calc
                const grandTotals = {}; svColumns.forEach(col => { grandTotals[col.id] = { metaFat: 0, metaVol: 0, metaPos: 0, avgVol: 0, avgMix: 0, metaMix: 0, avgFat: 0, monthlyValues: {} }; quarterMonths.forEach(m => grandTotals[col.id].monthlyValues[m.key] = 0); });

                sortedSupervisors.forEach((sup, index) => {
                    sup.id = `sup-${index}`;
                    svColumns.forEach(col => {
                        grandTotals[col.id].metaFat += sup.totals[col.id].metaFat; grandTotals[col.id].metaVol += sup.totals[col.id].metaVol; grandTotals[col.id].metaPos += sup.totals[col.id].metaPos;
                        grandTotals[col.id].avgVol += sup.totals[col.id].avgVol; grandTotals[col.id].avgMix += sup.totals[col.id].avgMix; grandTotals[col.id].metaMix += sup.totals[col.id].metaMix;
                        grandTotals[col.id].avgFat += sup.totals[col.id].avgFat;
                        if (sup.totals[col.id].monthlyValues) quarterMonths.forEach(m => grandTotals[col.id].monthlyValues[m.key] += sup.totals[col.id].monthlyValues[m.key]);
                    });

                    sup.sellers.sort((a, b) => (b.data['total_elma']?.metaFat || 0) - (a.data['total_elma']?.metaFat || 0));
                    sup.sellers.forEach(seller => {
                        bodyHTML += `<tr class="hover:bg-slate-800 border-b border-slate-800"><td class="px-2 py-1 text-center text-slate-400 font-mono">${seller.code}</td><td class="px-2 py-1 text-left text-white font-medium truncate max-w-[200px]" title="${seller.name}">${getFirstName(seller.name)}</td>`;
                        svColumns.forEach(col => {
                            const d = seller.data[col.id] || { metaFat: 0, metaVol: 0, metaPos: 0, avgVol: 0, avgMix: 0, metaMix: 0, avgFat: 0, monthlyValues: {} };
                            if (col.type === 'standard') {
                                const isReadOnly = col.isAgg; const inputClass = isReadOnly ? 'text-slate-400 font-bold opacity-70' : 'text-yellow-300'; const readonlyAttr = isReadOnly ? 'readonly' : ''; const cellBg = isReadOnly ? 'bg-[#151c36]' : 'bg-[#1e293b]';
                                quarterMonths.forEach(m => bodyHTML += `<td class="px-1 py-1 text-right text-slate-400 border-r border-slate-800/50 text-[10px] bg-blue-900/5">${(d.monthlyValues[m.key] || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>`);
                                bodyHTML += `<td class="px-1 py-1 text-right text-slate-300 border-r border-slate-800/50 bg-blue-900/10 font-medium">${d.avgFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 text-right ${col.colorClass} border-r border-slate-800/50 text-xs font-mono">${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 ${cellBg} border-r border-slate-800/50"><input type="text" value="${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}" class="goals-sv-input bg-transparent text-right w-full outline-none ${inputClass} text-xs font-mono" data-sup-id="${sup.id}" data-col-id="${col.id}" data-seller-id="${seller.id || seller.name.replace(/\s+/g,'_')}" data-field="fat" oninput="recalculateGoalsSvTotals(this)" ${readonlyAttr}></td><td class="px-1 py-1 text-center text-slate-300 border-r border-slate-800/50">${d.metaPos}</td><td class="px-1 py-1 ${cellBg} border-r border-slate-800/50"><input type="text" value="${d.metaPos}" class="goals-sv-input bg-transparent text-center w-full outline-none ${inputClass} text-xs font-mono" data-sup-id="${sup.id}" data-col-id="${col.id}" data-seller-id="${seller.id || seller.name.replace(/\s+/g,'_')}" data-field="pos" oninput="recalculateGoalsSvTotals(this)" ${readonlyAttr}></td>`;
                            } else if (col.type === 'tonnage') {
                                bodyHTML += `<td class="px-1 py-1 text-right text-slate-300 border-r border-slate-800/50">${d.avgVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-1 text-right text-slate-300 border-r border-slate-800/50 font-bold">${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-1 bg-[#1e293b] border-r border-slate-800/50"><input type="text" value="${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}" class="goals-sv-input bg-transparent text-right w-full outline-none text-yellow-300 text-xs font-mono" data-sup-id="${sup.id}" data-col-id="${col.id}" data-field="vol" oninput="recalculateGoalsSvTotals(this)"></td>`;
                            } else if (col.type === 'mix') {
                                bodyHTML += `<td class="px-1 py-1 text-right text-slate-300 border-r border-slate-800/50">${d.avgMix.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1})}</td><td class="px-1 py-1 text-right text-slate-300 border-r border-slate-800/50 font-bold">${d.metaMix}</td><td class="px-1 py-1 bg-[#1e293b] border-r border-slate-800/50"><input type="text" value="${d.metaMix}" class="goals-sv-input bg-transparent text-right w-full outline-none text-yellow-300 text-xs font-mono" data-sup-id="${sup.id}" data-col-id="${col.id}" data-field="mix" oninput="recalculateGoalsSvTotals(this)"></td>`;
                            } else if (col.type === 'geral') {
                                bodyHTML += `<td class="px-1 py-1 text-right text-slate-400 border-r border-slate-800/50 font-mono text-xs">${d.avgFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 text-right text-white font-bold border-r border-slate-800/50 font-mono text-xs goals-sv-text" data-sup-id="${sup.id}" data-col-id="geral" data-field="fat" id="geral-${seller.id || seller.name.replace(/\s+/g,'_')}-fat">${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 text-right text-white font-bold border-r border-slate-800/50 font-mono text-xs goals-sv-text" data-sup-id="${sup.id}" data-col-id="geral" data-field="ton" id="geral-${seller.id || seller.name.replace(/\s+/g,'_')}-ton">${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-1 text-center text-white font-bold border-r border-slate-800/50 font-mono text-xs goals-sv-text" data-sup-id="${sup.id}" data-col-id="geral" data-field="pos" id="geral-${seller.id || seller.name.replace(/\s+/g,'_')}-pos">${d.metaPos}</td>`;
                            } else if (col.type === 'pedev') {
                                bodyHTML += `<td class="px-1 py-1 text-center text-pink-400 font-bold border-r border-slate-800/50 font-mono text-xs goals-sv-text" data-sup-id="${sup.id}" data-col-id="pedev" data-field="pos" id="pedev-${seller.id || seller.name.replace(/\s+/g,'_')}-pos">${d.metaPos}</td>`;
                            }
                        });
                        bodyHTML += `</tr>`;
                    });

                    bodyHTML += `<tr class="bg-slate-800 font-bold border-b border-slate-600"><td class="px-2 py-2 text-center text-slate-400 font-mono">${sup.code}</td><td class="px-2 py-2 text-left text-white uppercase tracking-wider">${sup.name}</td>`;
                    svColumns.forEach(col => {
                        const d = sup.totals[col.id]; const color = col.id.includes('total') || col.type === 'tonnage' || col.type === 'mix' ? 'text-white' : 'text-slate-300';
                        if (col.type === 'standard') {
                            quarterMonths.forEach(m => bodyHTML += `<td class="px-1 py-1 text-right text-slate-400 border-r border-slate-700 text-[10px] bg-blue-900/5">${(d.monthlyValues[m.key] || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>`);
                            bodyHTML += `<td class="px-1 py-1 text-right text-slate-300 border-r border-slate-700 bg-blue-900/10 font-medium">${d.avgFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 text-right ${color} border-r border-slate-700">${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 text-right text-yellow-500/70 border-r border-slate-700" id="total-sup-${sup.id}-${col.id}-fat">${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 text-center ${color} border-r border-slate-700">${d.metaPos}</td><td class="px-1 py-1 text-center text-yellow-500/70 border-r border-slate-700" id="total-sup-${sup.id}-${col.id}-pos">${d.metaPos}</td>`;
                        } else if (col.type === 'tonnage') bodyHTML += `<td class="px-1 py-1 text-right text-slate-300 border-r border-slate-700">${d.avgVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-1 text-right ${color} border-r border-slate-700">${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-1 text-right text-yellow-500/70 border-r border-slate-700" id="total-sup-${sup.id}-${col.id}-vol">${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td>`;
                        else if (col.type === 'mix') bodyHTML += `<td class="px-1 py-1 text-right text-slate-300 border-r border-slate-700">${d.avgMix.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1})}</td><td class="px-1 py-1 text-right ${color} border-r border-slate-700">${d.metaMix}</td><td class="px-1 py-1 text-right text-yellow-500/70 border-r border-slate-700" id="total-sup-${sup.id}-${col.id}-mix">${d.metaMix}</td>`;
                        else if (col.type === 'geral') bodyHTML += `<td class="px-1 py-1 text-right text-slate-400 border-r border-slate-700">${d.avgFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 text-right text-white border-r border-slate-700" id="total-sup-${sup.id}-geral-fat">${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-1 text-right text-white border-r border-slate-700" id="total-sup-${sup.id}-geral-ton">${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-1 text-center text-white border-r border-slate-700" id="total-sup-${sup.id}-geral-pos">${d.metaPos}</td>`;
                        else if (col.type === 'pedev') bodyHTML += `<td class="px-1 py-1 text-center text-pink-400 border-r border-slate-700" id="total-sup-${sup.id}-pedev-pos">${Math.round(sup.totals['total_elma']?.metaPos * 0.9)}</td>`;
                    });
                    bodyHTML += `</tr>`;
                });

                // Grand Total
                bodyHTML += `<tr class="bg-[#0f172a] font-bold text-white border-t-2 border-slate-500 sticky bottom-0 z-20"><td class="px-2 py-3 text-center uppercase tracking-wider">GV</td><td class="px-2 py-3 text-left uppercase tracking-wider">Geral PRIME</td>`;
                svColumns.forEach(col => {
                    const d = grandTotals[col.id];
                    if (col.type === 'standard') {
                        quarterMonths.forEach(m => bodyHTML += `<td class="px-1 py-2 text-right text-slate-400 border-r border-slate-700 text-[10px] bg-blue-900/5">${(d.monthlyValues[m.key] || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>`);
                        bodyHTML += `<td class="px-1 py-2 text-right text-teal-400 border-r border-slate-700 bg-blue-900/10">${d.avgFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-2 text-right text-teal-400 border-r border-slate-700">${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-2 text-right text-teal-600/70 border-r border-slate-700" id="total-grand-${col.id}-fat">${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-2 text-center text-purple-400 border-r border-slate-700">${d.metaPos}</td><td class="px-1 py-2 text-center text-purple-600/70 border-r border-slate-700" id="total-grand-${col.id}-pos">${d.metaPos}</td>`;
                    } else if (col.type === 'tonnage') bodyHTML += `<td class="px-1 py-2 text-right text-slate-400 border-r border-slate-700">${d.avgVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-2 text-right text-orange-400 border-r border-slate-700">${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-2 text-right text-orange-600/70 border-r border-slate-700" id="total-grand-${col.id}-vol">${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td>`;
                    else if (col.type === 'mix') bodyHTML += `<td class="px-1 py-2 text-right text-slate-400 border-r border-slate-700">${d.avgMix.toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1})}</td><td class="px-1 py-2 text-right text-cyan-400 border-r border-slate-700">${d.metaMix}</td><td class="px-1 py-2 text-right text-cyan-600/70 border-r border-slate-700" id="total-grand-${col.id}-mix">${d.metaMix}</td>`;
                    else if (col.type === 'geral') bodyHTML += `<td class="px-1 py-2 text-right text-slate-500 border-r border-slate-700">${d.avgFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-2 text-right text-white border-r border-slate-700" id="total-grand-geral-fat">${d.metaFat.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td><td class="px-1 py-2 text-right text-white border-r border-slate-700" id="total-grand-geral-ton">${d.metaVol.toLocaleString('pt-BR', {minimumFractionDigits: 3, maximumFractionDigits: 3})}</td><td class="px-1 py-2 text-center text-white border-r border-slate-700" id="total-grand-geral-pos">${d.metaPos}</td>`;
                    else if (col.type === 'pedev') bodyHTML += `<td class="px-1 py-2 text-center text-pink-400 border-r border-slate-700" id="total-grand-pedev-pos">${Math.round(grandTotals['total_elma']?.metaPos * 0.9)}</td>`;
                });
                bodyHTML += `</tr></tbody>`;
                mainTable.innerHTML = headerHTML + bodyHTML;
            }, () => currentRenderId !== goalsSvRenderId);"""

        # Replace the function in content
        new_content = content[:start_idx] + new_function + content[func_end_idx+1:]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully patched 'updateGoalsSvView'")
    else:
        print("Could not find closing brace for the function body.")
else:
    print("Could not find the start or end marker of 'updateGoalsSvView'.")
