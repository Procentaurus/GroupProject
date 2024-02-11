import json
import os
import uuid
import csv

# Define the file path
output_file_path = os.path.join(os.path.dirname(__file__), '..\\fixtures\\basicCards.json')

# Convert Python data to JSON and save to file
def save_json_file(output_file_path, fixture_data_from_csv):
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []
    with open(output_file_path, 'w') as json_file:
        json.dump(fixture_data_from_csv, json_file, indent=4)
    
    # Append new data to the existing data
    existing_data.extend(fixture_data_from_csv)
    
    # Save the updated data back to the file
    with open(output_file_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

# Get reactionCard data from csv
def read_card_csv_generate_list(csv_file_path, model):
    fixture_data = []

    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            if model == 'gameMechanics.reactioncard':
                fixture_data.append({
                    "model": model,
                    "pk": str(uuid.uuid4()),
                    "fields": {
                        "name": row['name'],
                        "description": row['description'],
                        "cost": row['cost'],
                        "playerType": row['playerType'],
                        "type": row['type']
                    }
                })
            if model == 'gameMechanics.actioncard':
                fixture_data.append({
                    "model": model,
                    "pk": str(uuid.uuid4()),
                    "fields": {
                        "name": row['name'],
                        "description": row['description'],
                        "cost": row['cost'],
                        "playerType": row['playerType'],
                        "pressure": row['pressure']
                    }
                })
    
    return fixture_data

with open(file_path, 'w') as json_file:
    json.dump([], json_file)

reaction_list = read_card_csv_generate_list('gameMechanics/utils/reactionCard_data.csv', 'gameMechanics.reactioncard')
action_list = read_card_csv_generate_list('gameMechanics/utils/actionCard_data.csv', 'gameMechanics.actioncard')

save_json_file('gameMechanics/fixtures/cards.json', reaction_list)
save_json_file('gameMechanics/fixtures/cards.json', action_list)
