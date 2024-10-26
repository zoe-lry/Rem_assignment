# Commission Data Reconciliation

This script is designed to normalize commission data from multiple carriers and generate aggregated reports. The data is read from Excel files, transformed based on predefined mappings, and then saved to a CSV file.

## How to Run the Script

1. Create a Virtual Environment:

   ```
   python -m venv venv
   source venv/bin/activate
   ```

2. **Dependencies**: Ensure you have the necessary Python packages installed. You can install the required packages using:

   ```
   pip install pandas pyyaml openpyxl
   ```

3. **Run the Script**: To run the script, use the following command:

   ```
   python main.py
   ```
    The system will prompt you to enter the path for each commission data file and specify the corresponding carrier mapping.

4. **Output**: The script will generate a file named `normalized_commissions.csv` containing the combined and filtered commission data.

## Test Output
```
Enter the number of commission data files to process: 3

Processing file 1 of 3
Enter the file path of the commission data Excel file: data/Emblem%2006.2024%20Commission.xlsx
Enter the carrier name (e.g., Healthfirst, Centene, Emblem): emblem

Processing file 2 of 3
Enter the file path of the commission data Excel file: data/Centene%2006.2024%20Commission.xlsx
Enter the carrier name (e.g., Healthfirst, Centene, Emblem): centene

Processing file 3 of 3
Enter the file path of the commission data Excel file: data/Healthfirst%2006.2024%20Commission.xlsx
Enter the carrier name (e.g., Healthfirst, Centene, Emblem): healthfirst

Normalized data has been saved to 'normalized_commissions.csv'.

Top 10 Agents or Agencies by Commission Payout for June 2024:
   normalized_name  commission_amount
Kirk Carter-Thomas           30984.50
      Chelsea Corp           29467.09
    Brittany Smith           24335.44
     Patrick Evans           19811.64
        Laurie Lee           16490.27
  Jennifer Jackson           13209.94
      Samuel Ochoa           12889.79
     Javier Meyers           12872.46
    James Martinez           12202.30
       Kevin Parks           12172.78
```
## Assumptions

1. **Mapping Files**: Each carrier has a corresponding YAML mapping file located in the `mappings/` directory. The mapping file specifies how to transform the data from the carrier's Excel sheet to the desired format.

2. **Excel File Format**: The commission data is provided in Excel format (`.xlsx`). Each carrier file should have the correct structure, including all columns specified in the YAML mapping.

## Example YAML Mapping File

Here is an example of what a mapping file (e.g., `healthfirst.yaml`) might look like:

```
carrier_name: Healthfirst
sheet_name: HFStmtCommAtt
date_format: '%m/%Y'
fields:
  commission_period:
    source: Period
  carrier:
    type: fixed
    value: Healthfirst
  recipient_name:
    source: Producer Name
  recipient_type:
    source: Producer Type
  commission_amount:
    source: Amount
  member_id:
    source: Member ID
  member_name:
    source: Member Name
  policy_effective_date:
    source: Member Effective Date
  policy_termination_date:
    source: Disenrolled Date
  enrollment_type:
    source: Enrollment Type
  product_plan_name:
    source: Product
```

## Notes

- The final output CSV file (`normalized_commissions.csv`) contains combined data from all carriers, with columns standardized according to the mappings.

