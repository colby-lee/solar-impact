from data_collector.clients import NASAClient


client = NASAClient()

client.fetch_and_insert_solar_flares()



