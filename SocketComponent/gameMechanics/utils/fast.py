import pandas as pd

def update_image_paths(file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Update the 'image' column by adding the path using the 'name' column
    df['image'] = df['name'].apply(lambda x: f"card_images/{x.replace(' ', '_').lower()}.png")

    # Save the updated DataFrame back to the CSV file
    df.to_csv(file_path, index=False)

# Update the actionCard_data.csv file
update_image_paths('actionCard_data.csv')

# Update the reactionCard_data.csv file
update_image_paths('reactionCard_data.csv')
