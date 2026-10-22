/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

function utilColor(pct) {
    return pct >= 80 ? "critical" : "";
}

function rankClass(i) {
    return i === 0 ? "r1" : i === 1 ? "r2" : i === 2 ? "r3" : "rx";
}

class KpiCard extends Component {
    static template = "trdo_multi_warehouse.KpiCard";
    static props = ["icon", "iconClass", "value", "label"];
}

class WarehouseCard extends Component {
    static template = "trdo_multi_warehouse.WarehouseCard";
    static props = ["wh"];
}

class LowStockPanel extends Component {
    static template = "trdo_multi_warehouse.LowStockPanel";
    static props = ["items"];
}

class TopMoversPanel extends Component {
    static template = "trdo_multi_warehouse.TopMoversPanel";
    static props = ["items"];
    rankClass(i) { return rankClass(i); }
}

class RecentTransfersPanel extends Component {
    static template = "trdo_multi_warehouse.RecentTransfersPanel";
    static props = ["items"];
}

export class WarehouseDashboard extends Component {
    static template = "trdo_multi_warehouse.WarehouseDashboard";
    static components = { KpiCard, WarehouseCard, LowStockPanel, TopMoversPanel, RecentTransfersPanel };

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            refreshing: false,
            lastUpdated: null,
            summary: {},
            warehouses: [],
            top_movers: [],
            low_stock: [],
            recent_transfers: [],
        });
        onMounted(() => this.loadData());
    }

    async loadData(isRefresh = false) {
        if (isRefresh) {
            this.state.refreshing = true;
        } else {
            this.state.loading = true;
        }
        try {
            const data = await this.rpc("/trdo/warehouse/dashboard", {});
            this.state.summary = data.summary || {};
            this.state.warehouses = data.warehouses || [];
            this.state.top_movers = data.top_movers || [];
            this.state.low_stock = data.low_stock || [];
            this.state.recent_transfers = data.recent_transfers || [];
            this.state.lastUpdated = new Date().toLocaleTimeString();
        } catch (e) {
            this.notification.add("Failed to load dashboard data. Please try again.", {
                type: "danger",
                title: "Dashboard Error",
            });
        } finally {
            this.state.loading = false;
            this.state.refreshing = false;
        }
    }

    async onRefresh() {
        await this.loadData(true);
    }

    openWarehouseInventory(whId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Inventory",
            res_model: "stock.quant",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["location_id.usage", "=", "internal"]],
            context: { default_warehouse_id: whId },
        });
    }

    utilColor(pct) { return utilColor(pct); }
    rankClass(i) { return rankClass(i); }
}

registry.category("actions").add("trdo_warehouse_dashboard", WarehouseDashboard);
