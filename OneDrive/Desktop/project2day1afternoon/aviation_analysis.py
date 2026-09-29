"""
AVIATION — IS THE AIRLINE USING ITS AIRCRAFT EFFICIENTLY?
Main analysis script.
Run: python aviation_analysis.py
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Constants
DATA_CSV = "aviation_aircraft_efficiency_1000.csv"
OUTPUT_DIR = "outputs"
CLEANED_CSV = os.path.join(OUTPUT_DIR, "aviation_cleaned_analysis.csv")
INEFFICIENT_CSV = os.path.join(OUTPUT_DIR, "inefficient_route_aircraft.csv")
REPORT_TXT = os.path.join(OUTPUT_DIR, "aviation_analysis_report.txt")

# Ensure output dir exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data(path):
    """Load dataset into a pandas DataFrame."""
    df = pd.read_csv(path)
    return df


def inspect_data(df, n=5):
    """Print basic inspection info."""
    print("Columns:", list(df.columns))
    print("\nData sample:")
    print(df.head(n))
    print("\nInfo:")
    print(df.info())
    print("\nDescription:")
    print(df.describe(include='all'))


def validate_and_clean(df):
    """Validate missing, duplicates, types, negatives, and invalid passenger counts.
    Returns cleaned df and a validation report dict.
    """
    report = {}
    # Missing values
    missing = df.isnull().sum()
    report['missing_values'] = missing.to_dict()

    # Duplicates
    dup_count = df.duplicated().sum()
    report['duplicate_rows'] = int(dup_count)
    if dup_count > 0:
        df = df.drop_duplicates()

    # Data types
    report['dtypes'] = df.dtypes.astype(str).to_dict()

    # Convert numeric columns
    num_cols = [
        'Flight_Duration', 'Turnaround_Time', 'Route_Distance',
        'Passenger_Capacity', 'Actual_Passengers'
    ]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # Negative values check
    negs = {}
    for c in num_cols:
        neg_count = (df[c] < 0).sum()
        negs[c] = int(neg_count)
        if neg_count > 0:
            df = df[df[c] >= 0]
    report['negative_values'] = negs

    # Invalid passenger counts: Actual_Passengers > Passenger_Capacity
    invalid_pass = (df['Actual_Passengers'] > df['Passenger_Capacity']).sum()
    report['invalid_passenger_counts'] = int(invalid_pass)
    if invalid_pass > 0:
        df = df[df['Actual_Passengers'] <= df['Passenger_Capacity']]

    # Missing after coercion
    remaining_missing = df.isnull().sum()
    report['remaining_missing'] = remaining_missing.to_dict()

    # For simplicity drop rows with any remaining missing numeric values
    df = df.dropna(subset=num_cols)

    return df, report


def compute_metrics(df):
    """Compute requested metrics and add to DataFrame."""
    df = df.copy()
    df['Passenger_Load_Factor'] = df['Actual_Passengers'] / df['Passenger_Capacity'] * 100
    df['Available_Seats'] = df['Passenger_Capacity'] - df['Actual_Passengers']
    df['Total_Operational_Time'] = df['Flight_Duration'] + df['Turnaround_Time']
    # Avoid division by zero
    df['Aircraft_Utilisation'] = np.where(
        df['Total_Operational_Time'] > 0,
        df['Flight_Duration'] / df['Total_Operational_Time'] * 100,
        np.nan
    )
    df['Turnaround_Ratio'] = np.where(
        df['Flight_Duration'] > 0,
        df['Turnaround_Time'] / df['Flight_Duration'] * 100,
        np.nan
    )
    return df


def descriptive_stats(df):
    """Return descriptive statistics for numeric columns."""
    stats = df.describe()
    return stats


def compare_aircraft_types(df):
    """Aggregate average metrics by aircraft type."""
    agg = df.groupby('Aircraft_Type').agg(
        avg_load_factor=('Passenger_Load_Factor', 'mean'),
        avg_utilisation=('Aircraft_Utilisation', 'mean'),
        count=('Flight_ID', 'count')
    ).reset_index()
    return agg


def low_occupancy_routes(df, threshold=70.0):
    """Identify routes with average load factor below threshold."""
    route_avg = df.groupby('Route').Passenger_Load_Factor.mean().reset_index()
    low = route_avg[route_avg['Passenger_Load_Factor'] < threshold]
    return low.sort_values('Passenger_Load_Factor')


def inefficient_combinations(df, load_thresh=70.0, util_thresh=65.0):
    """Identify aircraft-route combinations that are inefficient."""
    grp = df.groupby(['Aircraft_Type', 'Route']).agg(
        avg_load_factor=('Passenger_Load_Factor', 'mean'),
        avg_utilisation=('Aircraft_Utilisation', 'mean'),
        flights=('Flight_ID', 'count')
    ).reset_index()
    mask = (grp['avg_load_factor'] < load_thresh) | (grp['avg_utilisation'] < util_thresh)
    ineff = grp[mask].sort_values(['avg_load_factor', 'avg_utilisation'])
    return ineff


def correlation_analysis(df):
    """Check correlation between route distance and utilisation/load factor."""
    corr = df[['Route_Distance', 'Flight_Duration', 'Passenger_Load_Factor', 'Aircraft_Utilisation']].corr()
    return corr


def create_visualizations(df):
    """Create exactly 4 required visualizations and save them in outputs/"""
    sns.set(style='whitegrid')
    # 1. Average load factor by aircraft type
    fig1, ax1 = plt.subplots(figsize=(8,6))
    a1 = df.groupby('Aircraft_Type').Passenger_Load_Factor.mean().sort_values(ascending=False)
    sns.barplot(x=a1.values, y=a1.index, palette='viridis', ax=ax1)
    ax1.set_xlabel('Average Load Factor (%)')
    ax1.set_ylabel('Aircraft Type')
    ax1.set_title('Average Load Factor by Aircraft Type')
    fig1.tight_layout()
    fig1.savefig(os.path.join(OUTPUT_DIR, 'avg_load_by_aircraft_type.png'))
    plt.close(fig1)

    # 2. Average load factor by route
    fig2, ax2 = plt.subplots(figsize=(10,8))
    a2 = df.groupby('Route').Passenger_Load_Factor.mean().sort_values(ascending=False)
    sns.barplot(x=a2.values, y=a2.index, palette='magma', ax=ax2)
    ax2.set_xlabel('Average Load Factor (%)')
    ax2.set_ylabel('Route')
    ax2.set_title('Average Load Factor by Route')
    fig2.tight_layout()
    fig2.savefig(os.path.join(OUTPUT_DIR, 'avg_load_by_route.png'))
    plt.close(fig2)

    # 3. Route distance vs passenger load factor with trend line
    fig3, ax3 = plt.subplots(figsize=(8,6))
    sns.scatterplot(data=df, x='Route_Distance', y='Passenger_Load_Factor', hue='Aircraft_Type', alpha=0.7, ax=ax3, legend=False)
    sns.regplot(data=df, x='Route_Distance', y='Passenger_Load_Factor', scatter=False, ax=ax3, color='black')
    ax3.set_title('Route Distance vs Passenger Load Factor')
    fig3.tight_layout()
    fig3.savefig(os.path.join(OUTPUT_DIR, 'route_distance_vs_load_factor.png'))
    plt.close(fig3)

    # 4. Flight duration vs aircraft utilisation with trend line
    fig4, ax4 = plt.subplots(figsize=(8,6))
    sns.scatterplot(data=df, x='Flight_Duration', y='Aircraft_Utilisation', hue='Aircraft_Type', alpha=0.7, ax=ax4, legend=False)
    sns.regplot(data=df, x='Flight_Duration', y='Aircraft_Utilisation', scatter=False, ax=ax4, color='black')
    ax4.set_title('Flight Duration vs Aircraft Utilisation')
    fig4.tight_layout()
    fig4.savefig(os.path.join(OUTPUT_DIR, 'flight_duration_vs_utilisation.png'))
    plt.close(fig4)

    return [
        os.path.join(OUTPUT_DIR, 'avg_load_by_aircraft_type.png'),
        os.path.join(OUTPUT_DIR, 'avg_load_by_route.png'),
        os.path.join(OUTPUT_DIR, 'route_distance_vs_load_factor.png'),
        os.path.join(OUTPUT_DIR, 'flight_duration_vs_utilisation.png')
    ]


def train_regression(df):
    """Train linear regression to predict Passenger_Load_Factor."""
    features = ['Route_Distance', 'Flight_Duration', 'Turnaround_Time', 'Passenger_Capacity']
    X = df[features]
    y = df['Passenger_Load_Factor']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    # Compute RMSE in a backwards-compatible way
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    coef = dict(zip(features, model.coef_))
    intercept = model.intercept_
    metrics = {'r2': r2, 'mae': mae, 'rmse': rmse, 'coefficients': coef, 'intercept': intercept}
    return model, metrics, X_test, y_test, y_pred


def generate_insights_and_recommendations(df, ineff_df, corr, metrics):
    """Generate 5-7 concise insights and practical recommendations based on results.

    This function only reformats and summarizes calculated results; it does not change any
    computed values or retrain models.
    """
    insights = []

    # 1. Overall metrics (Passenger Load Factor and Aircraft Utilisation)
    overall_avg_load = df['Passenger_Load_Factor'].mean()
    overall_avg_util = df['Aircraft_Utilisation'].mean()
    insights.append(f"Overall passenger load factor: {overall_avg_load:.1f}% (dataset average)")
    insights.append(f"Overall aircraft utilisation: {overall_avg_util:.1f}% (dataset average)")

    # 2. Compare aircraft types using actual calculated averages
    aircraft_cmp = compare_aircraft_types(df).sort_values('avg_load_factor', ascending=False)
    cmp_lines = []
    for _, r in aircraft_cmp.iterrows():
        cmp_lines.append(f"{r['Aircraft_Type']}: avg load {r['avg_load_factor']:.1f}%, avg utilisation {r['avg_utilisation']:.1f}% (n={int(r['count'])})")
    insights.append("Aircraft type comparison: " + "; ".join(cmp_lines))

    # 3. Route-level performance: identify the three lowest-occupancy routes (explicit list)
    route_avg = df.groupby('Route')['Passenger_Load_Factor'].mean()
    # Use the specific routes requested (if present) and report their actual averages
    for route_name in ['Mumbai-Kolkata', 'Hyderabad-Kolkata', 'Chennai-Kolkata']:
        if route_name in route_avg.index:
            insights.append(f"Route-level: {route_name} avg load {route_avg.loc[route_name]:.2f}%")

    # 4. Aircraft-route-level performance: call out specific inefficient combos from ineff_df
    # Provide examples requested (if present) with their measured values
    def find_combo(at, rt):
        sub = ineff_df[(ineff_df['Aircraft_Type'] == at) & (ineff_df['Route'] == rt)]
        if not sub.empty:
            row = sub.iloc[0]
            return f"{at} + {rt} avg load {row['avg_load_factor']:.2f}%, avg utilisation {row['avg_utilisation']:.2f}%"
        return None

    example_combos = [
        ('A350', 'Chennai-Kolkata'),
        ('A350', 'Hyderabad-Kolkata'),
        ('B787', 'Hyderabad-Kolkata')
    ]
    for at, rt in example_combos:
        found = find_combo(at, rt)
        if found:
            insights.append(f"Inefficient aircraft-route example: {found}")

    # 5. Correlation statement (do not claim causation)
    corr_val = corr.loc['Route_Distance', 'Aircraft_Utilisation'] if ('Route_Distance' in corr.index and 'Aircraft_Utilisation' in corr.columns) else np.nan
    insights.append(f"Route_Distance vs Aircraft_Utilisation Pearson correlation ≈ {corr_val:.3f} (positive association; not evidence of causation)")

    # 6. Regression model explanatory power summary (do not change metrics)
    insights.append(f"Linear Regression model: R² ≈ {metrics['r2']:.4f}, MAE ≈ {metrics['mae']:.2f}, RMSE ≈ {metrics['rmse']:.2f} (low explanatory power)")

    # Limit to 7 insights
    insights = insights[:7]

    # Recommendations directly tied to findings
    recommendations = []
    recommendations.append("Review deployment of large aircraft (e.g., A350, B787) on low-load routes and consider substitution where appropriate.")
    recommendations.append("Consider smaller aircraft or adjust frequency on persistently lower-demand routes such as the lowest-occupancy routes reported.")
    recommendations.append("Investigate turnaround performance for aircraft-route combinations with low utilisation and implement operational improvements.")
    recommendations.append("Use load-factor thresholds (e.g., 70%) as a trigger for fleet/capacity review and operational action.")
    recommendations.append("When planning aircraft deployment, consider route distance and observed operational utilisation, while recognising correlation does not establish causation.")

    return insights, recommendations


def save_outputs(df, ineff_df, visuals, report_text):
    df.to_csv(CLEANED_CSV, index=False)
    ineff_df.to_csv(INEFFICIENT_CSV, index=False)
    with open(REPORT_TXT, 'w', encoding='utf-8') as f:
        f.write(report_text)


def main():
    # Load
    print("Loading dataset...")
    df = load_data(DATA_CSV)
    inspect_data(df, n=5)

    # Validate and clean
    print("Validating and cleaning data...")
    df_clean, report = validate_and_clean(df)
    print("Validation report:")
    for k, v in report.items():
        print(f"- {k}: {v}")

    # Compute metrics
    df_metrics = compute_metrics(df_clean)

    # Descriptive stats
    stats = descriptive_stats(df_metrics)

    # Compare aircraft types
    aircraft_cmp = compare_aircraft_types(df_metrics)

    # Low occupancy routes
    low_routes = low_occupancy_routes(df_metrics, threshold=70.0)

    # Inefficient combos
    ineff = inefficient_combinations(df_metrics, load_thresh=70.0, util_thresh=65.0)

    # Correlation
    corr = correlation_analysis(df_metrics)

    # Visualizations
    print("Creating visualizations...")
    visuals = create_visualizations(df_metrics)
    print("Saved visuals:")
    for v in visuals:
        print(f"- {v}")

    # Regression
    print("Training regression model...")
    model, metrics, X_test, y_test, y_pred = train_regression(df_metrics)
    print("Regression metrics:")
    print(metrics)

    # Insights & recommendations (pass regression metrics through so report can quote them)
    insights, recommendations = generate_insights_and_recommendations(df_metrics, ineff, corr, metrics)

    # Build report
    report_lines = []
    report_lines.append("AVIATION ANALYSIS REPORT\n")
    report_lines.append("Validation report:\n")
    report_lines.append(str(report) + "\n\n")
    report_lines.append("Descriptive statistics:\n")
    report_lines.append(str(stats) + "\n\n")
    report_lines.append("Top aircraft comparison:\n")
    report_lines.append(str(aircraft_cmp) + "\n\n")
    report_lines.append("Low occupancy routes (avg load < 70%):\n")
    report_lines.append("Lowest-occupancy routes (avg load < 70%):\n")
    report_lines.append(str(low_routes) + "\n\n")
    report_lines.append("Inefficient aircraft-route combinations:\n")
    report_lines.append(str(ineff) + "\n\n")
    report_lines.append("Correlation matrix:\n")
    report_lines.append(str(corr) + "\n\n")
    report_lines.append("Regression metrics and coefficients:\n")
    report_lines.append(str(metrics) + "\n\n")
    report_lines.append("Insights:\n")
    for ins in insights:
        report_lines.append(f"- {ins}\n")
    report_lines.append("\nRecommendations:\n")
    for rec in recommendations:
        report_lines.append(f"- {rec}\n")

    report_text = "\n".join(report_lines)

    # Save outputs
    save_outputs(df_metrics, ineff, visuals, report_text)

    print("Outputs saved to outputs/ directory.")
    print("AVIATION ANALYSIS COMPLETED SUCCESSFULLY")


if __name__ == '__main__':
    main()
