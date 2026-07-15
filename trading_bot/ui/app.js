// UI Interactions & Operations
document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const navItems = document.querySelectorAll(".nav-item");
    const tabViews = document.querySelectorAll(".tab-view");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");

    const orderForm = document.getElementById("order-form");
    const orderTypeSelect = document.getElementById("order-type");
    const priceContainer = document.getElementById("price-container");
    const stopPriceContainer = document.getElementById("stop-price-container");
    const priceInput = document.getElementById("price");
    const stopPriceInput = document.getElementById("stop-price");
    const submitBtn = document.getElementById("submit-order-btn");
    const syncTimeBtn = document.getElementById("sync-time-btn");
    const consoleOutput = document.getElementById("console-output");
    const clearConsoleBtn = document.getElementById("clear-console-btn");
    const ordersTableBody = document.querySelector("#orders-table tbody");
    const historyTableBody = document.querySelector("#history-table tbody");
    const openOrdersCount = document.getElementById("open-orders-count");
    const emptyRow = document.getElementById("empty-row");
    const pingLatency = document.getElementById("ping-latency");
    const timeOffset = document.getElementById("time-offset");

    const clearHistoryBtn = document.getElementById("clear-history-btn");
    const saveSettingsBtn = document.getElementById("save-settings-btn");

    // State Variables
    let currentSide = "BUY";
    let activeOpenOrders = 1; // Start with the 1 demo order in HTML

    // --- TAB SWITCHING NAVIGATION ---
    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const targetId = item.getAttribute("data-target");

            // Toggle active menu class
            navItems.forEach(nav => nav.classList.remove("active"));
            item.classList.add("active");

            // Toggle active view panel
            tabViews.forEach(view => view.classList.add("d-none"));
            document.getElementById(targetId).classList.remove("d-none");

            // Update page headers dynamically
            if (targetId === "view-dashboard") {
                pageTitle.textContent = "Trading Dashboard";
                pageSubtitle.textContent = "Binance Futures (USDT-M) Testnet Gateway";
            } else if (targetId === "view-orders") {
                pageTitle.textContent = "Active Open Orders";
                pageSubtitle.textContent = "Currently active pending trades on the testnet";
            } else if (targetId === "view-history") {
                pageTitle.textContent = "Trade History Log";
                pageSubtitle.textContent = "Records of all filled, cancelled, or rejected order requests";
            } else if (targetId === "view-settings") {
                pageTitle.textContent = "System Configurations";
                pageSubtitle.textContent = "Manage API endpoints, keys, and execution limits";
            }
        });
    });

    // Toggle Order Side Colors
    document.getElementsByName("side").forEach(radio => {
        radio.addEventListener("change", (e) => {
            currentSide = e.target.value;
            if (currentSide === "BUY") {
                submitBtn.className = "btn btn-primary btn-block btn-buy-active";
                submitBtn.textContent = `Place BUY ${orderTypeSelect.value} Order`;
            } else {
                submitBtn.className = "btn btn-primary btn-block btn-sell-active";
                submitBtn.textContent = `Place SELL ${orderTypeSelect.value} Order`;
            }
        });
    });

    // Toggle Order Type Fields
    orderTypeSelect.addEventListener("change", (e) => {
        const type = e.target.value;
        
        // Update submit button text side action name
        if (currentSide === "BUY") {
            submitBtn.textContent = `Place BUY ${type} Order`;
        } else {
            submitBtn.textContent = `Place SELL ${type} Order`;
        }

        // Show/Hide relevant fields
        if (type === "LIMIT") {
            priceContainer.classList.remove("d-none");
            priceInput.required = true;
            stopPriceContainer.classList.add("d-none");
            stopPriceInput.required = false;
        } else if (type === "STOP_MARKET") {
            priceContainer.classList.add("d-none");
            priceInput.required = false;
            stopPriceContainer.classList.remove("d-none");
            stopPriceInput.required = true;
        } else {
            priceContainer.classList.add("d-none");
            priceInput.required = false;
            stopPriceContainer.classList.add("d-none");
            stopPriceInput.required = false;
        }
    });

    // Logger Utility
    function log(message, type = "info") {
        const line = document.createElement("div");
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        line.className = `log-line log-${type}`;
        line.textContent = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
        consoleOutput.appendChild(line);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    // Toast Notification Utility
    function showToast(message, status = "info") {
        const toast = document.createElement("div");
        toast.className = `toast toast-${status}`;
        
        let icon = '<i class="fa-solid fa-circle-info"></i>';
        if (status === "success") icon = '<i class="fa-solid fa-circle-check text-green"></i>';
        if (status === "error") icon = '<i class="fa-solid fa-triangle-exclamation text-red"></i>';

        toast.innerHTML = `${icon} <span>${message}</span>`;
        document.getElementById("toast-container").appendChild(toast);
        
        // Remove toast after 4 seconds
        setTimeout(() => {
            toast.style.animation = "slideIn 0.3s reverse forwards";
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Sync Server Time Simulation
    syncTimeBtn.addEventListener("click", () => {
        log("Dynamic calibration triggered: Fetching time sync from /fapi/v1/time...", "debug");
        syncTimeBtn.disabled = true;
        syncTimeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Syncing...';
        
        setTimeout(() => {
            const randomOffset = Math.floor(Math.random() * 40) - 160; 
            const randomLatency = Math.floor(Math.random() * 15) + 20; 
            
            timeOffset.textContent = `${randomOffset} ms`;
            pingLatency.textContent = `${randomLatency} ms`;
            
            log(`Time offset calculated successfully. Server offset: ${randomOffset} ms. Roundtrip Latency: ${randomLatency} ms.`, "info");
            showToast("Server time successfully synchronized!", "success");
            
            syncTimeBtn.disabled = false;
            syncTimeBtn.innerHTML = '<i class="fa-solid fa-rotate"></i> Sync Server Time';
        }, 800);
    });

    // Clear Console
    clearConsoleBtn.addEventListener("click", () => {
        consoleOutput.innerHTML = "";
    });

    // Clear History
    clearHistoryBtn.addEventListener("click", () => {
        historyTableBody.innerHTML = `<tr><td colspan="7" class="text-center" style="padding: 40px; color: var(--text-muted);">History cleared</td></tr>`;
        log("Order history log database cleared by user.", "warn");
        showToast("Order history cleared", "info");
    });

    // Save Settings
    saveSettingsBtn.addEventListener("click", () => {
        const key = document.getElementById("settings-api-key").value;
        log(`Updating API Credentials in-memory. New API Key loaded: ${key.substring(0, 8)}...`, "info");
        showToast("Credentials updated successfully!", "success");
    });

    // Order Placement Form Action
    orderForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const symbol = document.getElementById("symbol").value;
        const type = orderTypeSelect.value;
        const quantity = parseFloat(document.getElementById("quantity").value);
        const price = priceInput.value ? parseFloat(priceInput.value) : null;
        const stopPrice = stopPriceInput.value ? parseFloat(stopPriceInput.value) : null;

        // Visual validation feedback
        if (quantity <= 0) {
            showToast("Quantity must be greater than 0", "error");
            return;
        }

        log(`Order manager received parameters: symbol=${symbol}, side=${currentSide}, type=${type}, qty=${quantity}`, "debug");
        log(`Validating order parameters...`, "debug");

        // Simulate network API delay
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Placing Order...';

        setTimeout(() => {
            const orderId = Math.floor(Math.random() * 1000000) + 1572000000;
            const orderStatus = type === "LIMIT" || type === "STOP_MARKET" ? "NEW" : "FILLED";
            const avgPrice = type === "LIMIT" ? "0.00" : (type === "STOP_MARKET" ? "0.00" : (95000 + (Math.random() * 100 - 50)).toFixed(2));
            
            // Format log entries
            log(`Validation passed. Sending signed POST to /fapi/v1/order`, "info");
            log(`HTTP Request: POST /fapi/v1/order | Params: symbol=${symbol}, side=${currentSide}, type=${type}, qty=${quantity}, timestamp=${Date.now()}, signature=[REDACTED]`, "info");
            log(`HTTP Response: Status 200 | Order Placed successfully. ID: ${orderId}, Status: ${orderStatus}`, "info");

            showToast(`Order Placed! ID: ${orderId}`, "success");

            const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);

            // 1. Handle Active Open Orders list if pending/new
            if (orderStatus === "NEW") {
                const targetPrice = type === "LIMIT" ? `$${price.toLocaleString()}` : `Stop: $${stopPrice.toLocaleString()}`;
                
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="symbol-col">${symbol}</td>
                    <td><span class="badge-type">${type}</span></td>
                    <td><span class="${currentSide === 'BUY' ? 'text-green' : 'text-red'} text-bold">${currentSide}</span></td>
                    <td>${quantity}</td>
                    <td>${targetPrice}</td>
                    <td>
                        <button class="btn btn-icon btn-cancel" onclick="cancelOrder(this)">
                            <i class="fa-solid fa-trash-can"></i> Cancel
                        </button>
                    </td>
                `;
                ordersTableBody.appendChild(tr);
                
                activeOpenOrders++;
                openOrdersCount.textContent = activeOpenOrders;
                emptyRow.classList.add("d-none");
            } else {
                // 2. Direct MARKET Order filled immediately: Add to History Table directly
                const historyTr = document.createElement("tr");
                historyTr.innerHTML = `
                    <td>${timestamp}</td>
                    <td class="symbol-col">${symbol}</td>
                    <td>${type}</td>
                    <td><span class="${currentSide === 'BUY' ? 'text-green' : 'text-red'} text-bold">${currentSide}</span></td>
                    <td>${quantity}</td>
                    <td>$${parseFloat(avgPrice).toLocaleString()}</td>
                    <td><span class="badge badge-success">FILLED</span></td>
                `;
                // Add to top of history
                if (historyTableBody.firstElementChild && historyTableBody.firstElementChild.textContent.includes("History cleared")) {
                    historyTableBody.innerHTML = "";
                }
                historyTableBody.insertBefore(historyTr, historyTableBody.firstChild);
            }

            // Restore submit button
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
            orderForm.reset();
            
            // Reset visibility
            priceContainer.classList.add("d-none");
            stopPriceContainer.classList.add("d-none");
            priceInput.required = false;
            stopPriceInput.required = false;
        }, 1000);
    });
});

// Global Cancel Order handler (called from rows)
window.cancelOrder = function(button) {
    const row = button.closest("tr");
    const symbol = row.cells[0].textContent;
    const type = row.cells[1].textContent;
    const side = row.cells[2].textContent;
    const qty = row.cells[3].textContent;
    const priceStr = row.cells[4].textContent;
    
    // Simulate Cancel log
    const consoleOutput = document.getElementById("console-output");
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    
    const debugLine = document.createElement("div");
    debugLine.className = "log-line log-debug";
    debugLine.textContent = `[${timestamp}] [DEBUG] Cancelling open order for ${symbol} (${side})`;
    
    const requestLine = document.createElement("div");
    requestLine.className = "log-line log-info";
    requestLine.textContent = `[${timestamp}] [INFO] HTTP Request: DELETE /fapi/v1/order | Params: symbol=${symbol}, timestamp=${Date.now()}, signature=[REDACTED]`;
    
    const responseLine = document.createElement("div");
    responseLine.className = "log-line log-info";
    responseLine.textContent = `[${timestamp}] [INFO] HTTP Response: Status 200 | Order cancelled successfully.`;
    
    consoleOutput.appendChild(debugLine);
    consoleOutput.appendChild(requestLine);
    consoleOutput.appendChild(responseLine);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;

    // Toast
    const toast = document.createElement("div");
    toast.className = "toast toast-info";
    toast.innerHTML = `<i class="fa-solid fa-circle-info text-blue"></i> <span>Cancelled ${side} order on ${symbol}</span>`;
    document.getElementById("toast-container").appendChild(toast);
    setTimeout(() => {
        toast.style.animation = "slideIn 0.3s reverse forwards";
        setTimeout(() => toast.remove(), 300);
    }, 3000);

    // Add cancelled item to History Log table
    const historyTableBody = document.querySelector("#history-table tbody");
    const historyTr = document.createElement("tr");
    historyTr.innerHTML = `
        <td>${timestamp}</td>
        <td class="symbol-col">${symbol}</td>
        <td>${type}</td>
        <td><span class="${side === 'BUY' ? 'text-green' : 'text-red'} text-bold">${side}</span></td>
        <td>${qty}</td>
        <td>${priceStr}</td>
        <td><span class="badge" style="background-color: rgba(255, 61, 0, 0.1); color: var(--color-red); border: 1px solid rgba(255, 61, 0, 0.2);">CANCELLED</span></td>
    `;
    if (historyTableBody.firstElementChild && historyTableBody.firstElementChild.textContent.includes("History cleared")) {
        historyTableBody.innerHTML = "";
    }
    historyTableBody.insertBefore(historyTr, historyTableBody.firstChild);

    // Remove row
    row.remove();
    
    // Update counter
    const openOrdersCount = document.getElementById("open-orders-count");
    const count = parseInt(openOrdersCount.textContent) - 1;
    openOrdersCount.textContent = count;
    
    if (count === 0) {
        document.getElementById("empty-row").classList.remove("d-none");
    }
};
