import pandas as pd
import numpy as np

# Severity mapping dictionary based on crime classifications
severity_mapping = {
    # Severity 1-2: Minor violations and service calls
    'Bicycle Collision': 1,
    'Traffic Collision': 1,
    'Vehicle Collision': 1,
    'UNKNOWN Traffic Collision': 1,
    'MSR-Unfounded Traffic Collision': 1,
    'MSR - Vehicle Tow': 1,
    'MSR - Found Bicycle': 1,
    'MSR - Found Property': 1,
    'MSR-Found Property': 1,
    'MSR - Lost Property': 1,
    'MSR - Property & Evidence purge': 1,
    'MSR-Property & Evidence purge': 1,
    'MSR - Welfare Check': 1,
    'MSR-Welfare Check': 1,
    'MSR - Assist Citizen': 1,
    'MSR-Assist Citizen': 1,
    'MSR - Assist Students': 1,
    'MSR - Assist Fire Department': 1,
    'MSR - Assist Another Agency': 1,
    'MSR-Assist Other Agency': 1,
    'MSR - Medical Aid': 1,
    'MSR - Alcohol Poisoning': 1,
    'MSR-Alcohol Poisoning': 1,
    'MSR - Notice of Withdrawal from Property Issued': 1,
    'MSR - Notice of Withdrawal from Property Issued Trespassing': 1,
    'MSR-Notice of Withdrawal from Property Issued': 1,
    'MSR - Suspicious Circumstances': 1,
    'MSR - Suspicious Person': 1,
    'MSR-Suspicious Person': 1,
    'MSR-Suspicious Persons': 1,
    'MSR - Assist Hospital Staff': 1,
    'MSR-Assist Hospital': 1,
    'MSR-Assist Hospital Patient': 1,
    'MSR-Civil Dispute': 1,
    'MSR-Verbal Dispute': 1,
    'MSR - Report of Unfounded Assault': 1,
    'MSR-Report of Unfounded Assault': 1,
    'MSR - Allegations of Assault': 1,
    'MSR - Missing Person Report': 1,
    'MSR-Missing Person': 1,
    'MSR - Restraining Orders Served': 1,
    'MSR-Hate Speech': 1,
    'MSR - Firearm Surrendered for Destruction': 1,
    'MSR - Weapons Collected for Destruction': 1,
    'MSR - Ammunition for Destruction': 1,
    'MSR - Marijuana seized for destruction': 1,
    'MSR-Marijuana for Destruction': 1,
    'MSR - Medications for Destruction': 1,
    'MSR-Narcotics for destruction': 1,
    'MSR - Receive Firearm Parts': 1,
    'MSR-Found Property Stolen out of City of Davis': 1,
    'Appropriate Lost Property': 1,
    
    # Severity 3-4: Property crimes
    'Theft of a Bicycle': 3,
    'UNKNOWN Theft of a Bicycle': 3,
    'Attempted Theft of a Bicycle': 3,
    'Theft of Bicycle Parts': 3,
    'Theft from a Building': 4,
    'UNKNOWN Theft from a Building': 4,
    'Theft from a Building Shoplifting': 4,
    'Theft from a Building/Burglary': 4,
    'Theft from a Building/Credit Card Fraud': 4,
    'Theft from a Building/Vandalism': 4,
    'Theft from a Motor Vehicle': 4,
    'Theft from a Vehicle': 4,
    'Theft of Vehicle Parts': 4,
    'Theft of Vehicle Parts & Accessories': 4,
    'Theft of Vehicle Parts and Accessories - Other': 4,
    'Theft of Property': 4,
    'Theft - All Other': 4,
    'Theft All Other': 4,
    'Shoplifting': 3,
    'Stolen Vehicle - Other': 4,
    'Stolen Vehicle CASE PULLED IN ERROR': 4,
    'Vandalism': 3,
    'Vandalism to Vehicle': 3,
    'Vandalism to a Vehicle': 3,
    'Vandalism to an e-Scooter': 3,
    'Vehicle Vandalism': 3,
    'Vandalism/Stolen Vehicle': 4,
    'Vandalism/Tamper with Vehicle': 3,
    'Tamper with a Motor Vehicle': 3,
    'Tamper with a Fire Alarm': 3,
    'Fraud': 4,
    'Forge Vehicle Registration': 3,
    'Receive Stolen Property': 4,
    'Stolen Vehicle - Other/Weapon Law Violation/Possess Controlled Substance/Petty Theft/Concealed Weapon': 7,
    
    # Severity 5-6: Moderate offenses
    'Burglary': 5,
    'Burglary Theft from a Building': 5,
    'Burglary/Vandalism': 5,
    'Theft - All Other Burglary': 5,
    'DUI - Alcohol': 6,
    'DUI - Alcohol Bicycle/Fail to stop at Stop Sign': 6,
    'DUI Alcohol/Possess Controlled Substance': 6,
    'Driving Under the Influence': 6,
    'Fail to Stop/DUI-Alcohol': 6,
    'Driving with License Suspended/No Vehicle Registration/Possess Controlled Substance/Possess Paraphernalia/Fraud - Theft of ID': 6,
    'Suspended License/No Vehicle Registration': 5,
    'Possess Controlled Substance': 5,
    'Possess Controlled Substance/Possess Paraphernalia/Warrant': 5,
    'Possess Controlled Substance/Possess with more than 2 priors': 6,
    'P:ossess Controlled Substance/Priors/Warrants': 6,
    'Possess Paraphernalia': 5,
    'Possess Paraphernalia/Possess Illegally duplicated key to a Govt Building': 5,
    'Possess Narcotics': 5,
    'Simple Assault': 6,
    'Simple Assault - Dating Violence': 6,
    'Simple Assault on Officer/Simple Assault on Hospital Staff': 7,
    'Public Intoxication': 5,
    'Open Container/Minor in Possession of Alcohol/Open Container while driving': 5,
    'Warrant': 5,
    'Warrant/Possess Controlled Substance': 5,
    'Warrants': 5,
    'False ID/Drive w/o License': 5,
    'Use of University Facilities Not Open to Public/Obstruct Peace Officer/False ID': 5,
    'Attempted Extortion': 6,
    
    # Severity 7-8: Serious offenses
    'Aggravated Assault': 7,
    'Assault & Battery': 7,
    'Weapon Violation': 7,
    'Weapons Violation': 7,
    'Weapons Violation: Possess Metal Knuckles': 7,
    'Possess Loaded Firearm/Possess Undetectable Firearm': 8,
    'Possess Tear Gas by a Fellon': 7,
    'Vandalism: Hate Crime Anti Racial': 7,
    'Vandalism Vandalism: Hate Crime Anti Racial': 7,
    'Arson/Vandalism with Bias - Anti-Religion': 8,
    'Vandalism w/ Anti-Other Christian Bias': 7,
    'Stalking': 7,
    'Indecent Exposure': 7,
    'MSR - CSA Report: Allegation of Stalking': 7,
    'MSR - CSA Report: Allegations of Stalking': 7,
    'MSR-CSA Report: Allegation of Stalking': 7,
    'MSR - Suspicious Circumstances-Unwanted touching: Fondling Suspicious Circumstance': 8,
    
    # Severity 9-10: Most serious crimes
    'Rape/False Imprisonment/Dating Violence': 9,
    'Forcible Fondling': 9,
    'Allegations of Fondling Touch someone against their will-Fondling': 9,
    'MSR - CSA Report: Allegation of Fondling': 9,
    'MSR - CSA Report: Allegation of Fondling Rape': 10,
    'MSR - CSA Report: Allegation of Fondling/Rape': 10,
    'MSR - CSA Report: Allegations of Stalking & Fondling': 9,
    'MSR - CSA Report: Allegation of Rape': 10,
    'MSR - CSA Report: Allegation of Dating Violence': 8,
    'MSR - CSA Report: Allegation of Domestic Violence': 8,
    'MSR - CSA Report: Allegation of Hazing Allegation of Hazing and Fondling': 9,
    'MSR-CSA Report: Allegation of Hazing': 8,
    
    # Special cases - should be NaN
    'UNKNOWN': np.nan,
    'CASE NUMBER PULLED IN ERROR': np.nan,
}

df = pd.read_csv('../data/crimes_v1.csv')

# Keep only Davis crimes
df = df[df['Case Number'].str.startswith('C')]

df['severity'] = df['Report Classification'].map(severity_mapping)

# Check for any unmapped classifications
unmapped = df[df['severity'].isna() & df['Report Classification'].notna()]['Report Classification'].unique()
if len(unmapped) > 0:
    print(f"Warning: Found {len(unmapped)} unmapped classifications (will be set to NaN):")
    for classification in sorted(unmapped):
        print(f"  - {classification}")

print()
print(f"Severity column added. Distribution:")
print(df['severity'].value_counts().sort_index())

df.to_csv('../data/crimes_v2.csv', index=False)
print()
print("Updated CSV file saved with severity column!")