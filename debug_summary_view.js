            aggregateToAll('FOODS_ALL', ['1119_TODDYNHO', '1119_TODDY', '1119_QUAKER_KEROCOCO']);
            aggregateToAll('PEPSICO_ALL', ['707', '708', '752', '1119_TODDYNHO', '1119_TODDY', '1119_QUAKER_KEROCOCO']);

            // Calculate Averages and Finalize
            for (const key in metricsMap) {
                const m = metricsMap[key];

                m.avgFat = m.fat / QUARTERLY_DIVISOR;
                m.avgVol = m.vol / QUARTERLY_DIVISOR; // Kg
                m.prevVol = m.prevVol; // Kg

                m.prevClients = m.prevClientsSet.size;
                m.quarterlyPos = m.quarterlyPosClientsSet.size; // New Metric

                let sumClients = 0;
                m.monthlyClientsSets.forEach(set => sumClients += set.size);
                m.avgClients = sumClients / QUARTERLY_DIVISOR;
            }
            return metricsMap;
        }

        function updateGoalsSummaryView() {
            const container = document.getElementById('goals-summary-grid');
            if (!container) return;

            // Use the independent summary filter
            const displayMetrics = getMetricsForSupervisors(selectedGoalsSummarySupervisors);

            // Calculate Target Sums for Filtered Subset
            // 1. Identify clients matching the summary filter
            let filteredSummaryClients = allClientsData;

            // Apply "Active" Filter logic (Consistent with other Goal Views)
            filteredSummaryClients = filteredSummaryClients.filter(c => {
                const rca1 = String(c.rca1 || '').trim();
                const isAmericanas = (c.razaoSocial || '').toUpperCase().includes('AMERICANAS');
                if (isAmericanas) return true;
                // STRICT FILTER: Exclude RCA 53 (Balcão) variants and Empty/Inativos
                if (rca1 === '53' || rca1 === '053' || rca1 === '' || rca1 === 'INATIVOS') return false;
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

            // 2. Prepare Sets for fast lookup and Sum up goals
            const filteredSummaryClientCodes = new Set();
            const activeSellersInSummary = new Set();

            filteredSummaryClients.forEach(c => {
                filteredSummaryClientCodes.add(c['Código']);
                // Resolve Seller Name for Adjustment Filtering
                const rcaCode = String(c.rca1 || '').trim();
                if (rcaCode) {
                    const name = optimizedData.rcaNameByCode.get(rcaCode);
                    if (name) activeSellersInSummary.add(name);
                    else if (rcaCode === 'INATIVOS') activeSellersInSummary.add('INATIVOS');
                }
            });

            const summaryGoalsSums = {
                '707': { fat: 0, vol: 0 },
                '708': { fat: 0, vol: 0 },
                '752': { fat: 0, vol: 0 },
                '1119_TODDYNHO': { fat: 0, vol: 0 },
                '1119_TODDY': { fat: 0, vol: 0 },
                '1119_QUAKER_KEROCOCO': { fat: 0, vol: 0 }
            };

            // Calculate Base Total for Mix (Use ELMA_ALL metric with exclusion)
            const elmaTargetBase = getElmaTargetBase(displayMetrics, goalsPosAdjustments, activeSellersInSummary);

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
            const uniquePosClientsSet = new Set();

            const cardsHTML = summaryItems.map(item => {
                const key = item.supplier + (item.brand ? `_${item.brand}` : '');

                // Use calculated sums if filter is active, otherwise global targets?
                // Actually, if no filter is active, filteredSummaryClients = All Active, so the sum matches the global target.
                // So we can always use summaryGoalsSums.

                const target = summaryGoalsSums[key] || { fat: 0, vol: 0 };
                const metrics = displayMetrics[key] || { avgFat: 0, prevFat: 0 };

                let subCategoryAdjustment = 0;
                if (goalsPosAdjustments[key]) {
                    // goalsPosAdjustments keys are Seller Names, not Client Codes
                    goalsPosAdjustments[key].forEach((adjVal, sellerName) => {
                        if (activeSellersInSummary.has(sellerName)) {
                            subCategoryAdjustment += adjVal;
                        }
                    });
                }

                totalFat += target.fat;
                totalVol += target.vol;

                if (metrics.quarterlyPosClientsSet) {
                    metrics.quarterlyPosClientsSet.forEach(clientCode => uniquePosClientsSet.add(clientCode));
                }

                // Color mapping for classes
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
                                    <p class="text-xs text-slate-400 uppercase font-semibold">Meta Volume (Kg)</p>
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
                                    ${((metrics.quarterlyPos || 0) + subCategoryAdjustment).toLocaleString('pt-BR')}
                                </p>
                                <div class="flex justify-between text-[10px] text-slate-400 border-t border-slate-700/50 pt-1">
                                    <span>Ativos no Trimestre</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = cardsHTML;

            // Update Totals
            const totalFatEl = document.getElementById('summary-total-fat');
            const totalVolEl = document.getElementById('summary-total-vol');
            const totalPosEl = document.getElementById('summary-total-pos');
            const mixSaltyEl = document.getElementById('summary-mix-salty');
            const mixFoodsEl = document.getElementById('summary-mix-foods');

            if(totalFatEl) totalFatEl.textContent = totalFat.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            if(totalVolEl) totalVolEl.textContent = totalVol.toLocaleString('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 });

            // Calculate Base Total (Use PEPSICO_ALL metric instead of Union)
            // basePosCount is already defined at the top of the function

            let totalAdjustment = 0;
            // Only PEPSICO adjustments affect the Global/Summary Total Pos
            if (goalsPosAdjustments['PEPSICO_ALL']) {
                goalsPosAdjustments['PEPSICO_ALL'].forEach(val => totalAdjustment += val);
            }

            const adjustedTotalPos = basePosCount + totalAdjustment;

            if(totalPosEl) totalPosEl.textContent = adjustedTotalPos.toLocaleString('pt-BR');

            // Calculate base for Mix Goals (Exclude Americanas / Seller 1001)
            let naturalMixBaseCount = 0;
            uniquePosClientsSet.forEach(clientCode => {
                const client = clientMapForKPIs.get(String(clientCode));
                if (client) {
                     const rca1 = String(client.rca1 || '').trim();
                     if (rca1 !== '1001') {
                         naturalMixBaseCount++;
                     }
                }
            });

            // MIX KPIs - Based on ELMA Target (50% Salty / 30% Foods)
            const naturalSaltyTarget = Math.round(elmaTargetBase * 0.50);

            let mixSaltyAdjustment = 0;
            if (goalsMixSaltyAdjustments['PEPSICO_ALL']) {
                 goalsMixSaltyAdjustments['PEPSICO_ALL'].forEach((val, sellerName) => {
                     // Check if seller is in the filtered summary view
                     if (activeSellersInSummary.has(sellerName)) mixSaltyAdjustment += val;
                 });
            }
            if(mixSaltyEl) mixSaltyEl.textContent = (naturalSaltyTarget + mixSaltyAdjustment).toLocaleString('pt-BR');

            // Mix Foods - Based on ELMA Target (30%)
            const naturalFoodsTarget = Math.round(elmaTargetBase * 0.30);
            let mixFoodsAdjustment = 0;
            if (goalsMixFoodsAdjustments['PEPSICO_ALL']) {
                 goalsMixFoodsAdjustments['PEPSICO_ALL'].forEach((val, sellerName) => {
                     if (activeSellersInSummary.has(sellerName)) mixFoodsAdjustment += val;
                 });
            }
            if(mixFoodsEl) mixFoodsEl.textContent = (naturalFoodsTarget + mixFoodsAdjustment).toLocaleString('pt-BR');
        }

        function getElmaTargetBase(displayMetrics, goalsPosAdjustments, activeSellersSet) {
            // 1. Natural Base (Historical Positive Clients)
            let naturalCount = 0;
            const elmaMetrics = displayMetrics['ELMA_ALL'];

            if (elmaMetrics && elmaMetrics.quarterlyPosClientsSet) {
                elmaMetrics.quarterlyPosClientsSet.forEach(codCli => {
                    const client = clientMapForKPIs.get(String(codCli));
                    if (client) {
                        // Check if Americanas
                        const rca1 = String(client.rca1 || '').trim();
                        const isAmericanas = (client.razaoSocial || '').toUpperCase().includes('AMERICANAS');
                        // Exclude Americanas (RCA 1001) from the base
                        if (rca1 !== '1001' && !isAmericanas) {
                            naturalCount++;
                        }
                    }
                });
            }

            // 2. Adjustments (Meta Pos)
            let adjustment = 0;
            const elmaAdj = goalsPosAdjustments['ELMA_ALL'];
            if (elmaAdj) {
                elmaAdj.forEach((val, sellerName) => {
                    // Check if seller is in current view (activeSellersSet)
                    // AND not Americanas (Name check as adjustments are keyed by name)
                    const isAmericanasSeller = sellerName.toUpperCase().includes('AMERICANAS');

                    if ((!activeSellersSet || activeSellersSet.has(sellerName)) && !isAmericanasSeller) {
                        adjustment += val;
                    }
                });
            }

            return naturalCount + adjustment;
        }

                function calculateDistributedGoals(filteredClients, currentGoalsSupplier, currentGoalsBrand, goalFat, goalVol) {
            const cacheKey = currentGoalsSupplier + (currentGoalsBrand ? `_${currentGoalsBrand}` : '');

            if (quarterMonths.length === 0) identifyQuarterMonths();

            // Determine dates for Previous Month calc
            const currentDate = lastSaleDate;
            const prevMonthDate = new Date(Date.UTC(currentDate.getUTCFullYear(), currentDate.getUTCMonth() - 1, 1));
            const prevMonthIndex = prevMonthDate.getUTCMonth();
            const prevMonthYear = prevMonthDate.getUTCFullYear();

            // --- CÁLCULO DOS TOTAIS GLOBAIS (EMPRESA) PARA O FORNECEDOR/MARCA ATUAL ---
            let globalTotalAvgFat = 0;
