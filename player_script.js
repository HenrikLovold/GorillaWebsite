class Player {
    constructor (name) {
        this.name = name;
        this.cuts = [];
        this.purchases = [];
        this.deducts = [];
        this.misc = [];
    }

    addCuts (cuts_list) {

    }
}

const displayer = Vue.createApp({
    data () {
        return {
            players: {},
            player_names: [],
            player_names_current: [],
            selectedPlayer: null,
            searchInput: "",
            selectedPlayerObject: new Player("Dummy")
        };
    },

    methods: {
        async main () {
            const cuts = await this.loadFile("player_list.csv");
            const buy = await this.loadFile("buyer_list.csv")
            const deducts = await this.loadFile("deduct_list.csv")
            const misc = await this.loadFile("misc_list.csv")
            this.parsePlayers(cuts);
            this.parseCutsList(cuts);
            this.parseBuyerList(buy);
            this.parseDeductList(deducts);
            this.parseMiscList(misc);
        },

        async loadFile (filename) {
            try {
                const response = await fetch(filename);
                const result = await response.text();
                return result;
            }
            catch (error) {
                this.cuts_list.push({name: "Error:", values:error});
                return error;
            }
        },

        parsePlayers (result) {
            const lines = result.split(/\r?\n/);
            for (const line of lines) {
                if (line == "") {
                    continue
                }
                let index_of_bracket = line.indexOf("{") - 1;
                player_name = line.substring(0, index_of_bracket);
                this.players[player_name] = new Player(player_name);
                this.player_names.push(player_name)
            }
            this.player_names = Object.values(this.player_names).sort();
            this.player_names_current = [...this.player_names];
        },

        parseCutsList (result) {
            const lines = result.split(/\r?\n/);
            for (const line of lines) {
                if (line == "") {
                    continue
                }
                let index_of_bracket = line.indexOf("{") - 1;
                player_name = line.substring(0, index_of_bracket);
                player_cuts = line.substring(index_of_bracket+1);
                player_cuts = JSON.parse(player_cuts.replaceAll("'", "\""));
                this.players[player_name].cuts = player_cuts;
            }
        },

        parseBuyerList (result) {
            const lines = result.split(/\r?\n/);
            for (const line of lines) {
                if (line == "") {
                    continue
                }
                let index_of_bracket = line.indexOf("{") - 1;
                player_name = line.substring(0, index_of_bracket);
                purchases = line.substring(index_of_bracket+1);
                purchases = JSON.parse(purchases.replaceAll("'", "\""));
                if (this.players[player_name]) {
                    this.players[player_name].purchases = (purchases);
                }
            }
        },

        parseDeductList (result) {
            const lines = result.split(/\r?\n/);
            for (const line of lines) {
                if (line == "") {
                    continue
                }
                let index_of_bracket = line.indexOf("{") - 1;
                player_name = line.substring(0, index_of_bracket);
                deducts = line.substring(index_of_bracket+1);
                deducts = JSON.parse(deducts.replaceAll("'", "\""));
                if (this.players[player_name]) {
                    this.players[player_name].deducts = (deducts);
                }
            }
        },

        parseMiscList (result) {
            const lines = result.split(/\r?\n/);
            for (const line of lines) {
                if (line == "") {
                    continue
                }
                let index_of_bracket = line.indexOf("{") - 1;
                player_name = line.substring(0, index_of_bracket);
                misc = line.substring(index_of_bracket+1);
                misc = JSON.parse(misc.replaceAll("'", "\""));
                if (this.players[player_name]) {
                    this.players[player_name].misc = (misc);
                }
            }
        },

        sortData () {
            this.player_names.sort((a, b) => {
                const nameA = a.toUpperCase();
                const nameB = b.toUpperCase();
                if (nameA < nameB) {
                    return -1;
                }
                if (nameA > nameB) {
                    return 1;
                }
                if (nameA == nameB) {
                    return 0;
                }
            });
        },

        async limitToSearch () {
            let currentSearch = this.searchInput.toUpperCase();
            let results = [...this.player_names_current];
            if (!currentSearch || currentSearch == "") {
                results = [...this.player_names];
            } else {
                this.player_names_current = [...this.player_names];
                results = this.player_names_current.filter(item =>
                    item.toUpperCase().includes(currentSearch)
                );
            }
            this.player_names_current = results;
            this.sortData();
        },
    },

    mounted() {
        this.main();
    },

    watch: {
        searchInput(new_v, old_v) {
            this.limitToSearch();
        },

        selectedPlayer(new_v, old_v) {
            this.selectedPlayerObject = this.players[new_v];
        }
    },
});

displayer.mount("#app-root");