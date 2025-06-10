class Player {
    constructor (name) {
        this.name = name;
        this.cuts = []
        this.purchases = []
        this.deducts = []
        this.misc = []
    }

    addCuts (cuts_list) {

    }
}

const displayer = Vue.createApp({
    data () {
        return {
            players: {},
            player_names: [],
            selectedPlayer: null,
            searchInput: "",
            selectedPlayer: null

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
                this.players[player_name].cuts = ({ cuts:player_cuts });
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
                if (this.players[player_name]) {
                    this.players[player_name].purchases = ({ buys:purchases });
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
                if (this.players[player_name]) {
                    this.players[player_name].deducts = ({ deducts:deducts });
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
                if (this.players[player_name]) {
                    this.players[player_name].misc = ({ misc:misc });
                }
            }
        },

        sortData () {
            this.players.sort((a, b) => {
                const nameA = a.name.toUpperCase();
                const nameB = b.name.toUpperCase();
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
            let results = [...this.cuts_list];
            if (!currentSearch || currentSearch == "") {
                results = [...this.raw_player_list];
            } else {
                this.cuts_list = [...this.raw_player_list];
                results = this.cuts_list.filter(item =>
                    item.name.toUpperCase().includes(currentSearch)
                );
            }
            this.cuts_list = results;
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
            console.log(new_v)
        }
    },
});

displayer.mount("#app-root");