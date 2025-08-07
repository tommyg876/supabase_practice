from models import Client, Campaign  

class ROICalculator:
    def __init__(self, client: Client):
        self.client = client

    def calculate_total_roi(self):
        total_spend = 0
        total_mqls = 0
        total_target = 0
        
        for campaign in self.client.campaigns:
            total_spend += campaign.spend
            total_mqls += campaign.actual_mqls
            total_target += campaign.mql_target
        
        if total_target == 0:
            conversion_rate = 0
        else:
            conversion_rate = (total_mqls / total_target) * 100
            
        if total_mqls == 0:
            cost_per_mql = 0
        else:
            cost_per_mql = total_spend / total_mqls
            
        return {
            'total_spend': round(total_spend, 2),
            'total_mqls': total_mqls,
            'conversion_rate': round(conversion_rate, 1),
            'cost_per_mql': round(cost_per_mql, 2)
        }

    def get_best_performing_channel(self):
        if not self.client.campaigns:
            return None
            
        best_campaign = max(self.client.campaigns, key=lambda c: c.conversion_rate())
        return best_campaign.channel

# Example usage
client = Client(1, 'Acme Corp', 'acme@example.com', '2024-01-01')
google_campaign = Campaign('Q1 Google Ads', 5000, 100, 'Google Ads', 85)
facebook_campaign = Campaign('Q1 Facebook', 3000, 50, 'Facebook', 45)

client.add_campaign(google_campaign)
client.add_campaign(facebook_campaign)

calc = ROICalculator(client)
roi_data = calc.calculate_total_roi()
print(f"Total Spend: ${roi_data['total_spend']}")
print(f"Total MQLs: {roi_data['total_mqls']}")
print(f"Conversion Rate: {roi_data['conversion_rate']}%")
print(f"Cost per MQL: ${roi_data['cost_per_mql']}")