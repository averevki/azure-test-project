import os  

class Config:  
    # Get connection string from environment variable  
    DB_CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING', '')  
      
    # For production - Azure will inject PORT  
    PORT = int(os.environ.get("PORT", 5000))
