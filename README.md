# AirQual - AI-Based Air Quality Monitoring System

AirQual is a comprehensive air quality monitoring application that provides real-time AQI (Air Quality Index) tracking, interactive data visualization, and personalized health recommendations based on air quality levels.

![AirQual Dashboard](https://cdn-icons-png.flaticon.com/512/4107/4107793.png)

## Features

- 🌐 Real-time AQI monitoring for cities worldwide
- 📊 Interactive data visualization with Plotly
- 👤 User authentication system for personalized experience
- 📍 Multiple location tracking and bookmarking
- 📈 Historical AQI data analysis
- 🧠 AI-powered health recommendations based on air quality and personal health conditions
- 📱 Responsive design for all devices

## Technology Stack

- **Frontend/Backend**: Streamlit
- **Database**: PostgreSQL
- **Data Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: scikit-learn
- **API Integration**: World Air Quality Index (WAQI) API

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- WAQI API key (get one from https://aqicn.org/data-platform/token/)

### Setup Instructions

#### Option 1: Running on Replit

1. **Fork the Replit project**

2. **Set up environment secrets**

   In your Replit project:
   - Go to "Secrets" in the Tools menu
   - Add a new secret with key `WAQI_API_KEY` and your API key as the value
   - The PostgreSQL database is automatically configured in Replit

3. **Run the application**

   Click on the "Run" button to start the Streamlit server.
   The application will be available at the URL provided by Replit.

#### Option 2: Running Locally

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/airqual.git
   cd airqual
   ```

2. **Set up a virtual environment (optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install streamlit pandas plotly psycopg2-binary requests scikit-learn python-dotenv trafilatura
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory with the following variables:

   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/airqual
   WAQI_API_KEY=your_api_key_here
   ```

5. **Initialize the database**

   The application will automatically create the necessary tables when first run.

6. **Run the application**

   ```bash
   streamlit run app.py
   ```

   The application will be available at http://localhost:5000

## Project Structure

```
├── .streamlit/            # Streamlit configuration
│   └── config.toml
├── pages/                 # Streamlit pages
│   ├── dashboard.py
│   ├── history.py
│   ├── profile.py
│   └── recommendations.py
├── app.py                 # Main application entry point
├── auth.py                # Authentication system
├── data.py                # Air quality data fetching
├── database.py            # Database operations
├── models.py              # ML models for AQI prediction
├── utils.py               # Utility functions
└── recommendations.py     # Health recommendation system
```

## User Guide

### Registration and Login

1. On first access, you'll be prompted to register for an account
2. After registration, log in with your credentials
3. Your session will remain active until you log out

### Main Dashboard

- Enter a city name in the search bar to view its air quality data
- If a city isn't found, you'll see suggestions for similar cities
- The dashboard displays the current AQI with color-coded indicators
- You can save locations for quick access later

### Historical Data

- View historical AQI trends for a selected location
- Customize the date range to analyze specific periods
- View statistics such as average, maximum, and minimum AQI values

### Health Recommendations

- Receive general advice based on current air quality
- For personalized recommendations, enter your specific health conditions
- Get detailed advice for different groups (general population, sensitive groups, children, elderly)

## API Key Setup

This application uses the World Air Quality Index (WAQI) API to fetch real-time air quality data. To use your own API key:

1. Register for a free API key at https://aqicn.org/data-platform/token/
2. Add the key to your environment variables or .env file:
   ```
   WAQI_API_KEY=your_api_key_here
   ```

## Development

### Adding New Features

1. Fork the repository
2. Create a new branch for your feature
3. Add tests for your feature
4. Submit a pull request

### Running Tests

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- World Air Quality Index (WAQI) for providing the API
- Streamlit for the amazing web framework
- All contributors who have helped improve this project# ai-based-air-quality-monitoring
