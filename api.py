

from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import json_util # Helper to convert MongoDB BSON to JSON
import json

app = Flask(__name__)

# IMPORTANT: In a real app, get this from an environment variable
MONGO_URI = 'mongodb+srv://Scraper_use:2N49ArCe4RStECuU@marketplacecluster.yzch06m.mongodb.net/?retryWrites=true&w=majority&appName=MarketplaceCluster'
MONGO_DATABASE = 'marketplace_data'

client = MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]

@app.route('/api/company/<string:cin>', methods=['GET'])
def get_company(cin):
    try:
        # The spider name 'mca' becomes the collection name
        collection = db['mca'] 
        
        # Find the company by its CIN. The '_id' field is excluded from the result.
        company_data = collection.find_one({'cin': cin}, {'_id': 0})

        if company_data:
            return jsonify(company_data)
        else:
            return jsonify({'error': 'Company not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
