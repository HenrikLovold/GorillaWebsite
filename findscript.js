const displayer = Vue.createApp({
    data () {
        return {
            item_list: [],
            searchInput: "",
            raw_item_list: [],
            selectedItem: null,
            selectedName: "No item selected",
            selectedAvg: "Average price",
            priceList: null,
            currentPlot: "",
            bottomRightMaxHeight: "50vh"
        };
    },
    methods: {
        async main () {
            const result = await this.loadFile();
            this.parseAndAddData(result);
            this.sortData();
        },

        async loadFile () {
            let filename = "./out_list.csv";
            try {
                const response = await fetch(filename);
                const result = await response.text();
                return result;
            }
            catch (error) {
                this.item_list.push({name: "Error:", values:error});
                return error;
            }
        },

        parseAndAddData (result) {
            const lines = result.split(/\r?\n/);
            for (const line of lines) {
                if (line == "") {
                    continue
                }
                let index_of_bracket = line.indexOf("{") - 1;
                item_name = line.substring(0, index_of_bracket);
                item_prices = line.substring(index_of_bracket+1);
                this.raw_item_list.push({ name:item_name, values:item_prices });
            }
            this.item_list = [...this.raw_item_list];
        },

        sortData () {
            this.item_list.sort((a, b) => {
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
            let results = [...this.item_list];
            if (!currentSearch || currentSearch == "") {
                results = [...this.raw_item_list];
            } else {
                this.item_list = [...this.raw_item_list];
                results = this.item_list.filter(item =>
                    item.name.toUpperCase().includes(currentSearch)
                );
            }
            this.item_list = results;
            this.sortData();
        },

        async readDatesAndValues (item) {
            if (!item) {
                this.selectedName = "";
                this.selectedAvg = "";
                this.priceList = null;
                this.currentPlot = "";
                return;
            }
            item_name = item.name;
            item_values = item.values;
            const jsonString = item_values.replace(/'/g, '"');
            const dataObject = JSON.parse(jsonString);
            avg = dataObject["avg"];
            price_list = await this.generatePriceList(dataObject);
            await this.postDataToRightFields(item_name, avg, dataObject, price_list);
            await this.insertPlotForItem(item_name);
        },

        async generatePriceList (data_obj) {
            let dates = []
            Object.keys(data_obj).forEach(key => {
                const value = data_obj[key];
                if (key != "avg") {
                    dates.push({date:key, value:value});
                }
            })
            this.priceList = dates;
        },

        async postDataToRightFields (item_name, avg, price_list) {
            this.selectedName = item_name;
            this.selectedAvg = "Average price: " + avg + "g";
        },

        async insertPlotForItem (item_name) {
            item_name = item_name.replace(/ /g, "");
            path = "./plots/" + item_name + ".png";
            this.currentPlot = path;
        },

        updateBottomRightHeight() {
        this.$nextTick(() => {
            const header = document.querySelector("#header-content");
            const topRight = document.querySelector(".top-right");

            const headerHeight = header?.offsetHeight || 0;
            const topRightHeight = topRight?.offsetHeight || 0;
            const buffer = 15;

            const totalSubtract = headerHeight + topRightHeight + buffer;
            this.bottomRightMaxHeight = `calc(100vh - ${totalSubtract}px)`;
        });
    }
    },

    watch: {
        searchInput(new_v, old_v) {
            this.limitToSearch();
            this.updateBottomRightHeight();
        },

        selectedItem(new_v, old_v) {
            console.log(new_v)
            this.readDatesAndValues(new_v);
            this.updateBottomRightHeight();
        }
    },

    mounted() {
        this.main();
        this.updateBottomRightHeight();
    }
});

displayer.mount("#app-root");