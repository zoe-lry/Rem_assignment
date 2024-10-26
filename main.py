import pandas as pd
import yaml
import os

# Function to standardize names
def standardize_name(name):
    if pd.isnull(name):
        return ''
    name = name.lower().strip()
    # Remove middle names/initials
    parts = name.split()
    if len(parts) > 2:
        name = f"{parts[0]} {parts[-1]}"
    # Remove titles like Jr, Sr, III
    if parts[-1] in ['jr', 'sr', 'ii', 'iii', 'iv']:
        name = ' '.join(parts[:-1])
    return name.title()

# Function to load YAML mapping
def load_mapping(carrier_name):
    mapping_file = f"mappings/{carrier_name.lower()}.yaml"
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as f:
            mapping = yaml.safe_load(f)
            return mapping
    else:
        print(f"Mapping file for '{carrier_name}' not found.")
        return None

# Function to normalize data based on mapping
def normalize_data(mapping, file_path):
    try:
        df = pd.read_excel(
            file_path,
            sheet_name=mapping.get('sheet_name', 0)
        )
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading '{file_path}': {e}")
        return None

    normalized_data = {}
    for field, specs in mapping['fields'].items():
        if 'type' in specs and specs['type'] == 'fixed':
            # Fixed value field
            normalized_data[field] = specs['value']
        elif 'type' in specs and specs['type'] == 'conditional':
            # Conditional field
            conditions = specs['conditions']
            source_field = specs['source']
            def map_conditional_field(x):
                for cond in conditions:
                    if 'value' in cond and x == cond['value']:
                        return cond['result']
                return conditions[-1]['default']
            normalized_data[field] = df[source_field].apply(map_conditional_field)
        elif 'type' in specs and specs['type'] == 'date':
            # Date field
            normalized_data[field] = pd.to_datetime(
                df[specs['source']],
                format=specs.get('format'),
                errors='coerce'
            )
        elif 'source' in specs:
            source = specs['source']
            if isinstance(source, list):
                # Concatenate multiple columns
                missing_columns = [col for col in source if col not in df.columns]
                if missing_columns:
                    print(f"Columns {missing_columns} not found in '{file_path}'.")
                    return None
                normalized_data[field] = df[source].apply(
                    lambda x: ' '.join(x.dropna().astype(str)), axis=1
                )
            else:
                if source not in df.columns:
                    print(f"Column '{source}' not found in '{file_path}'.")
                    return None
                normalized_data[field] = df[source]

        else:
            # Handle other types if necessary
            normalized_data[field] = None

    normalized_df = pd.DataFrame(normalized_data)

    # Standardize recipient names with first name and last name only
    normalized_df['normalized_name'] = normalized_df['recipient_name'].apply(standardize_name)

    # Format commission period
    if 'date_format' in mapping:
        date_format = mapping['date_format']
        if 'commission_period' in normalized_df.columns:
            normalized_df['commission_period'] = pd.to_datetime(
                normalized_df['commission_period'],
                format=date_format,
                errors='coerce'
            ).dt.strftime('%m/%Y')
    else:
        normalized_df['commission_period'] = normalized_df['commission_period']

    return normalized_df

# Main function
def main():
    all_normalized_data = []
    carrier_list = []

    num_files = int(input("Enter the number of commission data files to process: "))

    for i in range(num_files):
        print(f"\nProcessing file {i+1} of {num_files}")
        file_path = input("Enter the file path of the commission data Excel file: ").strip()
        carrier_name = input("Enter the carrier name (e.g., Healthfirst, Centene, Emblem): ").strip()
        mapping = load_mapping(carrier_name)
        if mapping:
            normalized_df = normalize_data(mapping, file_path)
            all_normalized_data.append(normalized_df)
            carrier_list.append(carrier_name)
        else:
            print(f"Skipping file '{file_path}' due to missing mapping.")

    # carrier_list = [
    #     {'file_path': 'data/Emblem%2006.2024%20Commission.xlsx', 'carrier_name': 'emblem'},
    #     {'file_path': 'data/Centene%2006.2024%20Commission.xlsx', 'carrier_name': 'centene'},
    #     {'file_path': 'data/Healthfirst%2006.2024%20Commission.xlsx', 'carrier_name': 'healthfirst'}
    # ]
    # for carrier in carrier_list:
    #     file_path = carrier['file_path']
    #     carrier_name = carrier['carrier_name']
    #     print(f"\nProcessing file: {file_path}")
    #     mapping = load_mapping(carrier_name)
    #     if mapping:
    #         normalized_df = normalize_data(mapping, file_path)
    #         all_normalized_data.append(normalized_df)
    #     else:
    #         print(f"Skipping file '{file_path}' due to missing mapping.")


    if not all_normalized_data:
        print("No data to process. Exiting.")
        return
    
    # Combine all normalized data
    try:
        df_combined = pd.concat(all_normalized_data, ignore_index=True)
    except ValueError as e:
        print(f"Error combining data: {e}")
        return

    # Save all normalized data to CSV before filtering
    df_combined.to_csv('normalized_commissions.csv', index=False)
    print("\nNormalized data has been saved to 'normalized_commissions.csv'.")

    # filter data for June 2024 for calculating top 10
    df_june_2024 = df_combined[df_combined['commission_period'] == '06/2024']

    # Filter for Delta Care Corporation or agents (if applicable)
    df_filtered = df_june_2024[
        df_june_2024['recipient_type'].str.contains('Broker|Agent|Agency', case=False, na=False)
    ]

    # Aggregate commissions
    df_aggregated = df_filtered.groupby(['normalized_name'])['commission_amount'].sum().reset_index()

    # Sort and get top 10
    df_top10 = df_aggregated.sort_values('commission_amount', ascending=False).head(10)

    # Output the results
    print("\nTop 10 Agents or Agencies by Commission Payout for June 2024:")
    print(df_top10.to_string(index=False))


if __name__ == '__main__':
    main()
