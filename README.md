# 🍳 Recipe Finder

A modern recipe search application built with Streamlit, featuring data from TheMealDB API and PostgreSQL database storage.

## ✨ Features

- **🔍 Smart Search**: Search by recipe name, ingredients, category, or area
- **📱 Responsive Interface**: Modern web interface built with Streamlit
- **🖼️ Rich Display**: Includes recipe images, ingredients, cooking steps, and detailed information
- **🗄️ Data Persistence**: Uses PostgreSQL to store recipe data
- **📄 Detailed View**: Click on any recipe to view full details with ingredients and instructions
- **🎨 Modern Design**: Beautiful card-based layout with hover effects

## 🛠️ Tech Stack

- **Frontend**: Streamlit, HTML/CSS, Pillow
- **Backend**: Python 3.8+, SQLAlchemy, PostgreSQL
- **Data Source**: TheMealDB API (free, no API key required)

## 📁 Project Structure

```
recipe-shuffle/
├── 📁 backend/                    # Backend services
│   ├── 📁 core/                   # Core business logic
│   │   ├── config.py              # Configuration management
│   │   └── models.py              # Database models and connections
│   ├── 📁 services/               # Business services
│   │   ├── data_service.py        # Data service layer
│   │   └── recommendation_service.py  # Recommendation engine
│   └── 📁 api/                    # External API integration
│       └── client.py              # TheMealDB API client
│
├── 📁 frontend/                   # Frontend interface
│   └── app.py                     # Streamlit main application
│
├── 📁 scripts/                    # Scripts and tools
│   ├── 📁 sync/                   # Data synchronization
│   │   ├── quick_sync.py          # Quick data sync
│   │   ├── daily_sync.py          # Daily sync script
│   │   └── smart_sync.py          # Smart sync script
│   ├── 📁 admin/                  # Administrative tools
│   │   ├── admin_tools.py         # Admin tools and testing
│   │   └── test_app.py            # Application testing
│   └── setup.py                   # Setup script
│
├── requirements.txt               # Dependencies list
├── env_example.env               # Environment variables example
├── run.py                        # Main startup script
└── README.md                     # Project documentation
```

## 📊 Database Schema

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| meal_id | String | TheMealDB ID |
| name | String | Recipe name |
| category | String | Category |
| area | String | Area/Region |
| instructions | Text | Cooking instructions |
| image_url | String | Image URL |
| youtube_url | String | YouTube link |
| ingredients | Array | Ingredients list |
| measures | Array | Measurements list |
| tags | Array | Tags list |
| created_at | DateTime | Creation time |
| updated_at | DateTime | Update time |

## 📄 License

MIT License

## 🙏 Acknowledgments

- [TheMealDB](https://www.themealdb.com/) - Free recipe API
- [Streamlit](https://streamlit.io/) - Python web framework  
- [PostgreSQL](https://www.postgresql.org/) - Open-source database