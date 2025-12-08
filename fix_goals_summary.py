import re

file_path = 'EXPORTADOR DASH V7.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target function signature
start_marker = "function updateGoalsSummaryView() {"
# End marker (a distinct line near the end of the function)
end_marker = "if(mixFoodsEl) mixFoodsEl.textContent = Math.round(mixBaseCount * 0.30).toLocaleString('pt-BR');"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx != -1 and end_idx != -1:
    brace_idx = content.find("}", end_idx)
    if brace_idx != -1:
        # The replacement function code
        new_function = r"""function updateGoalsSummaryView() {
            const container = document.getElementById('goals-summary-grid');
            if (!container) return;

            const displayMetrics = getMetricsForSupervisors(selectedGoalsSummarySupervisors);

            // 1. Identify clients matching the summary filter
            let filteredSummaryClients = allClientsData.filter(c => {
                const rca1 = String(c.rca1 || '').trim();
                const isAmericanas = (c.razaoSocial || '').toUpperCase().includes('AMERICANAS');
                if (isAmericanas) return true;
                if (rca1 === '53') return false;
                return true;
            });

            if (selectedGoalsSummarySupervisors.length > 0) {
                const supervisorsSet = new Set(selectedGoalsSummarySupervisors);
                const rcasSet = new Set();
                supervisorsSet.forEach(sup => {
                    (optimizedData.rcasBySupervisor.get(sup) || []).forEach(rca => rcasSet.add(rca));
                });
                filteredSummaryClients = filteredSummaryClients.filter(c => c.rcas.some(r => rcasSet.has(r)));
            }

            // 2. Sum up FINANCIAL goals (unchanged)
            const summaryGoalsSums = {
                '707': { fat: 0, vol: 0 },
                '708': { fat: 0, vol: 0 },
                '752': { fat: 0, vol: 0 },
                '1119_TODDYNHO': { fat: 0, vol: 0 },
                '1119_TODDY': { fat: 0, vol: 0 },
                '1119_QUAKER_KEROCOCO': { fat: 0, vol: 0 }
            };

            filteredSummaryClients.forEach(c => {
                const codCli = c['Código'];
                if (globalClientGoals.has(codCli)) {
                    const cGoals = globalClientGoals.get(codCli);
                    cGoals.forEach((val, key) => {
                        if (summaryGoalsSums[key]) {
                            summaryGoalsSums[key].fat += val.fat;
                            summaryGoalsSums[key].vol += val.vol;
                        }
                    });
                }
            });

            // 3. Calculate EFFECTIVE POSITIVATION GOALS (Natural + Overrides)
            const targetKeys = ['707', '708', '752', '1119_TODDYNHO', '1119_TODDY', '1119_QUAKER_KEROCOCO', 'ELMA_ALL', 'FOODS_ALL'];
            const sellerNaturalCounts = new Map(); // Map<SellerName, Map<Key, Count>>
            const activeSellers = new Set();

            // Helper to normalize strings
            const norm = (str) => str ? str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase() : '';

            // Build Natural Baselines from Filtered Clients
            filteredSummaryClients.forEach(c => {
                const rcaCode = c.rcas[0];
                const sellerName = optimizedData.rcaNameByCode.get(rcaCode) || rcaCode;
                activeSellers.add(sellerName);

                if (!sellerNaturalCounts.has(sellerName)) sellerNaturalCounts.set(sellerName, new Map());
                const sellerCounts = sellerNaturalCounts.get(sellerName);

                const hIds = optimizedData.indices.history.byClient.get(c['Código']);
                if(hIds) {
                    const clientSums = {};
                    hIds.forEach(id => {
                        const s = optimizedData.historyById.get(id);
                        if (s.TIPOVENDA === '1' || s.TIPOVENDA === '9') {
                            const codFor = String(s.CODFOR);
                            const desc = norm(s.DESCRICAO || '');
                            const keysToAdd = [];

                            if (codFor === '707') { keysToAdd.push('707'); keysToAdd.push('ELMA_ALL'); }
                            else if (codFor === '708') { keysToAdd.push('708'); keysToAdd.push('ELMA_ALL'); }
                            else if (codFor === '752') { keysToAdd.push('752'); keysToAdd.push('ELMA_ALL'); }
                            else if (codFor === '1119') {
                                keysToAdd.push('FOODS_ALL');
                                if (desc.includes('TODDYNHO')) keysToAdd.push('1119_TODDYNHO');
                                else if (desc.includes('TODDY')) keysToAdd.push('1119_TODDY');
                                else if (desc.includes('QUAKER') || desc.includes('KEROCOCO')) keysToAdd.push('1119_QUAKER_KEROCOCO');
                            }

                            keysToAdd.forEach(k => {
                                clientSums[k] = (clientSums[k] || 0) + s.VLVENDA;
                            });
                        }
                    });

                    for (const k in clientSums) {
                        if (clientSums[k] > 1) {
                            sellerCounts.set(k, (sellerCounts.get(k) || 0) + 1);
                        }
                    }
                }
            });

            // Include Sellers with Overrides (even if no natural clients in filter)
            const isSellerAllowed = (name) => {
                if (selectedGoalsSummarySupervisors.length === 0) return true;
                let code = optimizedData.rcaCodeByName.get(name);
                // Find which supervisor owns this code
                for (const [supName, rcas] of optimizedData.rcasBySupervisor) {
                     if (selectedGoalsSummarySupervisors.includes(supName) && rcas.includes(code)) return true;
                }
                return false;
            };

            for (const sellerName in globalSellerGoals) {
                if (!activeSellers.has(sellerName) && isSellerAllowed(sellerName)) {
                    activeSellers.add(sellerName);
                }
            }

            // Aggregate Effective Totals
            const effectiveTotals = {};
            targetKeys.forEach(k => effectiveTotals[k] = 0);

            activeSellers.forEach(sellerName => {
                const naturalCounts = sellerNaturalCounts.get(sellerName) || new Map();
                const overrides = globalSellerGoals[sellerName] || {};

                targetKeys.forEach(key => {
                    let val = naturalCounts.get(key) || 0;
                    if (overrides[key]) {
                        val = overrides[key].pos;
                    }
                    effectiveTotals[key] += val;
                });
            });

            const summaryItems = [
                { title: 'Extrusados', supplier: '707', brand: null, color: 'teal' },
                { title: 'Não Extrusados', supplier: '708', brand: null, color: 'blue' },
                { title: 'Torcida', supplier: '752', brand: null, color: 'purple' },
                { title: 'Toddynho', supplier: '1119', brand: 'TODDYNHO', color: 'orange' },
                { title: 'Toddy', supplier: '1119', brand: 'TODDY', color: 'amber' },
                { title: 'Quaker / Kerococo', supplier: '1119', brand: 'QUAKER_KEROCOCO', color: 'cyan' }
            ];

            let totalFat = 0;
            let totalVol = 0;

            const cardsHTML = summaryItems.map(item => {
                const key = item.supplier + (item.brand ? `_${item.brand}` : '');

                const target = summaryGoalsSums[key] || { fat: 0, vol: 0 };
                const metrics = displayMetrics[key] || { avgFat: 0, prevFat: 0 };

                totalFat += target.fat;
                totalVol += target.vol;

                const colorMap = {
                    teal: 'border-teal-500 text-teal-400 bg-teal-900/10',
                    blue: 'border-blue-500 text-blue-400 bg-blue-900/10',
                    purple: 'border-purple-500 text-purple-400 bg-purple-900/10',
                    orange: 'border-orange-500 text-orange-400 bg-orange-900/10',
                    amber: 'border-amber-500 text-amber-400 bg-amber-900/10',
                    cyan: 'border-cyan-500 text-cyan-400 bg-cyan-900/10'
                };

                const styleClass = colorMap[item.color] || colorMap.teal;
                const textColor = styleClass.split(' ')[1];

                // Use Effective Pos
                const effectivePos = effectiveTotals[key] || 0;
                // Use Natural for comparison display
                const naturalPos = metrics.quarterlyPos || 0;

                return `
                    <div class="bg-[#1e2a5a] border-l-4 ${styleClass.split(' ')[0]} rounded-r-lg p-4 shadow-md transition hover:-translate-y-1">
                        <h3 class="font-bold text-lg text-white mb-3 border-b border-slate-700 pb-2">${item.title}</h3>
                        <div class="space-y-4">
                            <div>
                                <div class="flex justify-between items-baseline mb-1">
                                    <p class="text-xs text-slate-400 uppercase font-semibold">Meta Faturamento</p>
                                </div>
                                <p class="text-xl font-bold ${textColor} mb-2">
                                    ${target.fat.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </p>
                                <div class="flex justify-between text-[10px] text-slate-400 border-t border-slate-700/50 pt-1">
                                    <span>Trim: <span class="text-slate-300">${metrics.avgFat.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span></span>
                                    <span>Ant: <span class="text-slate-300">${metrics.prevFat.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span></span>
                                </div>
                            </div>

                            <div>
                                <div class="flex justify-between items-baseline mb-1">
                                    <p class="text-xs text-slate-400 uppercase font-semibold">Meta Volume (Ton)</p>
                                </div>
                                <p class="text-xl font-bold ${textColor} mb-2">
                                    ${target.vol.toLocaleString('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 })}
                                </p>
                                <div class="flex justify-between text-[10px] text-slate-400 border-t border-slate-700/50 pt-1">
                                    <span>Trim: <span class="text-slate-300">${metrics.avgVol.toLocaleString('pt-BR', { minimumFractionDigits: 3 })}</span></span>
                                    <span>Ant: <span class="text-slate-300">${metrics.prevVol.toLocaleString('pt-BR', { minimumFractionDigits: 3 })}</span></span>
                                </div>
                            </div>

                            <div>
                                <div class="flex justify-between items-baseline mb-1">
                                    <p class="text-xs text-slate-400 uppercase font-semibold">Meta Pos. (Clientes)</p>
                                </div>
                                <p class="text-xl font-bold ${textColor} mb-2">
                                    ${effectivePos.toLocaleString('pt-BR')}
                                </p>
                                <div class="flex justify-between text-[10px] text-slate-400 border-t border-slate-700/50 pt-1">
                                    <span>Ativos no Trimestre (Nat: ${naturalPos})</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = cardsHTML;

            const totalFatEl = document.getElementById('summary-total-fat');
            const totalVolEl = document.getElementById('summary-total-vol');
            const totalPosEl = document.getElementById('summary-total-pos');
            const mixSaltyEl = document.getElementById('summary-mix-salty');
            const mixFoodsEl = document.getElementById('summary-mix-foods');

            if(totalFatEl) totalFatEl.textContent = totalFat.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            if(totalVolEl) totalVolEl.textContent = totalVol.toLocaleString('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 });

            // Total Meta Pos = Sum of ELMA + FOODS effective goals
            const totalPosCount = (effectiveTotals['ELMA_ALL'] || 0) + (effectiveTotals['FOODS_ALL'] || 0);
            if(totalPosEl) totalPosEl.textContent = totalPosCount.toLocaleString('pt-BR');

            // Mix Base (Exclude Americanas)
            let mixBase = 0;
            activeSellers.forEach(sellerName => {
                const code = optimizedData.rcaCodeByName.get(sellerName) || '';
                if (code !== '1001') {
                     const overrides = globalSellerGoals[sellerName] || {};
                     const naturalCounts = sellerNaturalCounts.get(sellerName) || new Map();

                     let elma = naturalCounts.get('ELMA_ALL') || 0;
                     if (overrides['ELMA_ALL']) elma = overrides['ELMA_ALL'].pos;

                     let foods = naturalCounts.get('FOODS_ALL') || 0;
                     if (overrides['FOODS_ALL']) foods = overrides['FOODS_ALL'].pos;

                     mixBase += (elma + foods);
                }
            });

            if(mixSaltyEl) mixSaltyEl.textContent = Math.round(mixBase * 0.60).toLocaleString('pt-BR');
            if(mixFoodsEl) mixFoodsEl.textContent = Math.round(mixBase * 0.30).toLocaleString('pt-BR');
        }"""

        new_content = content[:start_idx] + new_function + content[brace_idx+1:]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully patched 'updateGoalsSummaryView'")
    else:
        print("Could not find closing brace for the function.")
else:
    print("Could not find the start or end of the target function.")
