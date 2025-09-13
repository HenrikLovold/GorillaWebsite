
class Player:

    def __init__(self, name, raids=[], purchases=[], cuts=[]):
        self.name = name
        self.raids = raids
        self.purchases = purchases
        self.cuts = cuts
        self.sum_purchases = 0
        self.sum_cuts = 0

    def update_purchases(self):
        self.sum_purchases = 0
        for purchase in self.purchases:
            self.sum_purchases += purchase
    
    def update_cuts(self):
        self.sum_cuts = 0
        for cut in self.cuts:
            self.sum_cuts += cut

    def add_raid(self, raid_name):
        self.raids.append(raid_name)