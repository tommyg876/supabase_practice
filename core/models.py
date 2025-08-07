class Client:
    def __init__(self, id, name, email, start_date):
        self.id = id
        self.name = name
        self.email = email
        self.start_date = start_date
        self.campaigns = []
    
    def add_campaign(self, campaign):
        self.campaigns.append(campaign)
    
    def __str__(self):
        campaign_list = ", ".join(str(c) for c in self.campaigns)
        return f"{self.name} has campaigns: {campaign_list}"

class Campaign:
    def __init__(self, campaign_name, spend, mql_target, channel, actual_mqls=0):
        self.campaign_name = campaign_name
        self.spend = spend
        self.mql_target = mql_target
        self.channel = channel
        self.actual_mqls = actual_mqls
    
    def conversion_rate(self):
        if self.mql_target == 0:
            return 0
        return (self.actual_mqls / self.mql_target) * 100

    def cost_per_mql(self):
        if self.actual_mqls == 0:
            return 0
        return self.spend / self.actual_mqls

    def __str__(self):
        return f"{self.campaign_name} ({self.channel}): ${self.spend} | Target: {self.mql_target} | Actual: {self.actual_mqls}"