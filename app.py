from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# Load the datasets with error handling
try:
    covid_data = pd.read_csv('covid_19_data.csv')
    liver_cancer_data = pd.read_csv('effects_on_liver_cancer.csv')
    education_data = pd.read_csv('impact_on_education.csv', on_bad_lines='skip')  # Skip bad lines
    vaccination_data = pd.read_csv('vaccination.csv')
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

# Set matplotlib backend to avoid GUI conflicts
import matplotlib
matplotlib.use('Agg')

# Function to generate the chart for top 20 affected countries
def plot_top_countries():
    plt.figure(figsize=(12, 6))
    top_20 = covid_data.groupby('Country/Region')['Confirmed'].sum().sort_values(ascending=False).head(20)
    ax = top_20.plot(kind='bar', color=['#C96868','#FADFA1','#7EACB5','#A5B68D','#CDC1FF'])

    # Add percentage on top of bars
    for p in ax.patches:
        percentage = '{:.1f}%'.format((p.get_height() / covid_data['Confirmed'].sum()) * 100)
        ax.annotate(percentage, (p.get_x() + p.get_width() / 2, p.get_height()), 
                    ha='center', va='bottom')

    # Set labels and title
    plt.xlabel('Country/Region')
    plt.ylabel('Total Confirmed Cases (in millions)')
    plt.xticks(rotation=45)
    plt.legend(['Confirmed Cases'], loc='upper right')  # Move scale to top-right
    plt.tight_layout()
    plt.savefig('static/top_20_countries.png')
    plt.close()

# Function to analyze liver cancer data
def plot_liver_cancer():
    plt.figure(figsize=(10, 6))
    ax = liver_cancer_data.groupby('Alive_Dead').size().plot(kind='bar', color=['#FFB0B0','#A1D6B2'])

    # Add percentage on top of bars
    for p in ax.patches:
        percentage = '{:.1f}%'.format((p.get_height() / liver_cancer_data.shape[0]) * 100)
        ax.annotate(percentage, (p.get_x() + p.get_width() / 2, p.get_height()), 
                    ha='center', va='bottom')

    # Set labels and title
    plt.xlabel('Status')
    plt.ylabel('Number of Cases (in millions)')
    plt.xticks(rotation=0)
    plt.legend(['Liver Cancer Impact'], loc='upper right')  # Move scale to top-right
    plt.tight_layout()
    plt.savefig('static/liver_cancer_impact.png')
    plt.close()

# Function to analyze education data
def plot_education_impact():
    plt.figure(figsize=(8, 6))
    ax = education_data.groupby('Status')['Country'].count().plot(kind='bar', color=['#C96868','#FADFA1','#7EACB5','#A5B68D','#CDC1FF'])

    # Add percentage on top of bars
    total = education_data.shape[0]
    for p in ax.patches:
        percentage = '{:.1f}%'.format((p.get_height() / total) * 100)
        ax.annotate(percentage, (p.get_x() + p.get_width() / 2, p.get_height()), 
                    ha='center', va='bottom')

    # Set labels and title
    plt.xlabel('Education Status')
    plt.ylabel('Count (in millions)')
    plt.xticks(rotation=0)
    plt.legend(['Education Impact'], loc='upper right')  # Move scale to top-right
    plt.tight_layout()
    plt.savefig('static/education_impact.png')
    plt.close()

# Function to analyze vaccination data
def plot_vaccination_status():
    plt.figure(figsize=(10, 6))
    top_20_vaccinations = vaccination_data.groupby('country')['total_vaccinations'].sum().sort_values(ascending=False).head(20)
    ax = top_20_vaccinations.plot(kind='bar', color=['#C96868','#FADFA1','#7EACB5','#A5B68D','#CDC1FF'])

    # Add percentage on top of bars
    total_vaccinations = vaccination_data['total_vaccinations'].sum()
    for p in ax.patches:
        percentage = '{:.1f}%'.format((p.get_height() / total_vaccinations) * 100)
        ax.annotate(percentage, (p.get_x() + p.get_width() / 2, p.get_height()), 
                    ha='center', va='bottom')

    # Set labels and title
    plt.xlabel('Country')
    plt.ylabel('Total Vaccinations (in millions)')
    plt.xticks(rotation=45)
    plt.legend(['Total Vaccinations'], loc='upper right')  # Move scale to top-right
    plt.tight_layout()
    plt.savefig('static/vaccination_status.png')
    plt.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    plot_top_countries()
    plot_liver_cancer()
    plot_education_impact()
    plot_vaccination_status()

    countries = covid_data['Country/Region'].unique()

    selected_country = None
    if request.method == 'POST':
        selected_country = request.form['country']
        country_data = covid_data[covid_data['Country/Region'] == selected_country]
        
        # Plot for selected country COVID-19 confirmed cases over time (line chart)
        if not country_data.empty:
            plt.figure(figsize=(10, 6))
            country_data_grouped = country_data.groupby('Country/Region').agg({'Confirmed': 'sum','Deaths': 'sum','Recovered': 'sum','Active': 'sum'}).reset_index()
            country_data_grouped.plot(kind='line', color='#1f77b4')
            plt.xlabel('Death (in millions)')
            plt.ylabel('Confirmed Cases (in millions)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('static/covid_data_country.png')
            plt.close()

        # Liver cancer, education, and vaccination plots for selected country (if data available)

        education_country = education_data[education_data['Country'] == selected_country]
        if not education_country.empty:
            plt.figure(figsize=(10, 6))
            education_country.groupby('Date')['Status'].count().plot(kind='line', color='#2ca02c')
            plt.xlabel('Date')
            plt.ylabel('Impact Count (in millions)')
            plt.tight_layout()
            plt.savefig('static/education_country.png')
            plt.close()

        vaccination_country = vaccination_data[vaccination_data['country'] == selected_country]
        if not vaccination_country.empty:
            plt.figure(figsize=(10, 6))
            vaccination_country.groupby('date')['total_vaccinations'].sum().plot(kind='line', color='#d62728')
            plt.xlabel('Date')
            plt.ylabel('Total Vaccinations (in millions)')
            plt.tight_layout()
            plt.savefig('static/vaccination_country.png')
            plt.close()

        return render_template('analysis.html', selected_country=selected_country, countries=countries)

    return render_template('analysis.html', countries=countries)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True) 