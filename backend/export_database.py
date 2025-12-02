#!/usr/bin/env python
"""
Database Export Utility
Exports MongoDB collections to various formats (JSON, CSV, Excel)
Usage: python export_database.py [options]
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


class DatabaseExporter:
    """Handles exporting MongoDB collections to various formats."""
    
    def __init__(self, mongo_uri: str = None, db_name: str = None):
        """
        Initialize the exporter.
        
        Args:
            mongo_uri: MongoDB connection URI
            db_name: Database name
        """
        self.mongo_uri = mongo_uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
        self.db_name = db_name or os.getenv('MONGODB_DB', 'student_management')
        self.client = None
        self.db = None
        self.export_dir = Path('exports')
        self.export_dir.mkdir(exist_ok=True)
    
    def connect(self):
        """Establish MongoDB connection."""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {self.db_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("✅ MongoDB connection closed")
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get document count for each collection."""
        stats = {}
        collections = self.db.list_collection_names()
        
        for collection_name in collections:
            count = self.db[collection_name].count_documents({})
            stats[collection_name] = count
        
        return stats
    
    def export_to_json(self, collection_name: str, query: Dict = None, 
                       filename: str = None, pretty: bool = True) -> str:
        """
        Export collection to JSON file.
        
        Args:
            collection_name: Name of the collection to export
            query: MongoDB query filter (optional)
            filename: Output filename (optional)
            pretty: Format JSON with indentation
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{collection_name}_{timestamp}.json"
        
        filepath = self.export_dir / filename
        
        try:
            collection = self.db[collection_name]
            cursor = collection.find(query or {})
            
            # Convert ObjectId to string and handle datetime
            documents = []
            for doc in cursor:
                doc_copy = doc.copy()
                if '_id' in doc_copy:
                    doc_copy['_id'] = str(doc_copy['_id'])
                
                # Convert datetime objects to ISO format
                for key, value in doc_copy.items():
                    if isinstance(value, datetime):
                        doc_copy[key] = value.isoformat()
                
                documents.append(doc_copy)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(documents, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(documents, f, ensure_ascii=False)
            
            print(f"✅ Exported {len(documents)} documents to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Failed to export {collection_name} to JSON: {str(e)}")
            raise
    
    def export_to_csv(self, collection_name: str, query: Dict = None, 
                      filename: str = None, flatten: bool = True) -> str:
        """
        Export collection to CSV file.
        
        Args:
            collection_name: Name of the collection to export
            query: MongoDB query filter (optional)
            filename: Output filename (optional)
            flatten: Flatten nested objects
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{collection_name}_{timestamp}.csv"
        
        filepath = self.export_dir / filename
        
        try:
            collection = self.db[collection_name]
            cursor = collection.find(query or {})
            
            documents = list(cursor)
            
            if not documents:
                print(f"⚠️ No documents found in {collection_name}")
                return str(filepath)
            
            # Process documents
            processed_docs = []
            for doc in documents:
                doc_copy = doc.copy()
                
                # Convert ObjectId to string
                if '_id' in doc_copy:
                    doc_copy['_id'] = str(doc_copy['_id'])
                
                # Convert datetime to string
                for key, value in doc_copy.items():
                    if isinstance(value, datetime):
                        doc_copy[key] = value.isoformat()
                    elif isinstance(value, list) and flatten:
                        # Convert lists to JSON strings
                        doc_copy[key] = json.dumps(value) if value else ""
                    elif isinstance(value, dict) and flatten:
                        # Flatten nested objects
                        for nested_key, nested_value in value.items():
                            doc_copy[f"{key}_{nested_key}"] = nested_value
                        del doc_copy[key]
                
                processed_docs.append(doc_copy)
            
            # Get all unique keys
            all_keys = set()
            for doc in processed_docs:
                all_keys.update(doc.keys())
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(processed_docs)
            
            print(f"✅ Exported {len(processed_docs)} documents to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Failed to export {collection_name} to CSV: {str(e)}")
            raise
    
    def export_to_excel(self, collection_name: str, query: Dict = None, 
                       filename: str = None, sheet_name: str = None) -> str:
        """
        Export collection to Excel file.
        
        Args:
            collection_name: Name of the collection to export
            query: MongoDB query filter (optional)
            filename: Output filename (optional)
            sheet_name: Excel sheet name (optional)
            
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{collection_name}_{timestamp}.xlsx"
        
        if not sheet_name:
            sheet_name = collection_name
        
        filepath = self.export_dir / filename
        
        try:
            collection = self.db[collection_name]
            cursor = collection.find(query or {})
            
            documents = list(cursor)
            
            if not documents:
                print(f"⚠️ No documents found in {collection_name}")
                return str(filepath)
            
            # Process documents for DataFrame
            processed_docs = []
            for doc in documents:
                doc_copy = doc.copy()
                
                # Convert ObjectId to string
                if '_id' in doc_copy:
                    doc_copy['_id'] = str(doc_copy['_id'])
                
                # Handle different data types
                for key, value in doc_copy.items():
                    if isinstance(value, datetime):
                        doc_copy[key] = value.isoformat()
                    elif isinstance(value, (dict, list)):
                        doc_copy[key] = json.dumps(value, default=str)
                
                processed_docs.append(doc_copy)
            
            # Create DataFrame and export
            df = pd.DataFrame(processed_docs)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"✅ Exported {len(processed_docs)} documents to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Failed to export {collection_name} to Excel: {str(e)}")
            raise
    
    def export_all_collections(self, format: str = 'json', query: Dict = None):
        """
        Export all collections in the database.
        
        Args:
            format: Export format (json, csv, excel)
            query: MongoDB query filter (optional)
        """
        collections = self.db.list_collection_names()
        
        if not collections:
            print("⚠️ No collections found in database")
            return
        
        print(f"\n📦 Exporting {len(collections)} collections to {format.upper()}...")
        
        exported_files = []
        for collection_name in collections:
            try:
                if format.lower() == 'json':
                    filepath = self.export_to_json(collection_name, query)
                elif format.lower() == 'csv':
                    filepath = self.export_to_csv(collection_name, query)
                elif format.lower() == 'excel':
                    filepath = self.export_to_excel(collection_name, query)
                else:
                    print(f"❌ Unsupported format: {format}")
                    continue
                
                exported_files.append(filepath)
                
            except Exception as e:
                print(f"❌ Failed to export {collection_name}: {str(e)}")
        
        print(f"\n✅ Exported {len(exported_files)} collections successfully")
        return exported_files
    
    def create_backup_manifest(self, exported_files: List[str]) -> str:
        """
        Create a manifest file with export metadata.
        
        Args:
            exported_files: List of exported file paths
            
        Returns:
            Path to manifest file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        manifest_path = self.export_dir / f"backup_manifest_{timestamp}.json"
        
        manifest = {
            "backup_info": {
                "timestamp": datetime.now().isoformat(),
                "database": self.db_name,
                "mongo_uri": self.mongo_uri.replace(self.mongo_uri.split('@')[-1].split('/')[0], '***'),
                "total_files": len(exported_files),
                "exported_by": "export_database.py"
            },
            "collection_stats": self.get_collection_stats(),
            "exported_files": []
        }
        
        for filepath in exported_files:
            file_path = Path(filepath)
            if file_path.exists():
                manifest["exported_files"].append({
                    "filename": file_path.name,
                    "size_bytes": file_path.stat().st_size,
                    "format": file_path.suffix[1:],  # Remove the dot
                    "exported_at": datetime.now().isoformat()
                })
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created backup manifest: {manifest_path}")
        return str(manifest_path)


def main():
    """Main function to handle command-line arguments and execute exports."""
    parser = argparse.ArgumentParser(
        description="Export MongoDB collections to various formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export all collections to JSON
  python export_database.py --format json --all
  
  # Export specific collection to CSV
  python export_database.py --collection students --format csv
  
  # Export with query filter
  python export_database.py --collection students --format json --query '{"final_grade": {"$gte": 70}}'
  
  # Export to Excel with custom filename
  python export_database.py --collection students --format excel --output my_students.xlsx
        """
    )
    
    parser.add_argument(
        '--collection', '-c',
        help='Specific collection to export (default: all collections)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv', 'excel'],
        default='json',
        help='Export format (default: json)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output filename (default: auto-generated with timestamp)'
    )
    
    parser.add_argument(
        '--query', '-q',
        help='MongoDB query filter as JSON string (e.g., \'{"final_grade": {"$gte": 70}}\')'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Export all collections'
    )
    
    parser.add_argument(
        '--list-collections', '-l',
        action='store_true',
        help='List all collections and exit'
    )
    
    parser.add_argument(
        '--mongo-uri',
        help='MongoDB connection URI (overrides .env)'
    )
    
    parser.add_argument(
        '--db-name',
        help='Database name (overrides .env)'
    )
    
    args = parser.parse_args()
    
    # Initialize exporter
    exporter = DatabaseExporter(args.mongo_uri, args.db_name)
    
    # Connect to database
    if not exporter.connect():
        sys.exit(1)
    
    try:
        # List collections if requested
        if args.list_collections:
            stats = exporter.get_collection_stats()
            print("\n📊 Collections in database:")
            for collection, count in stats.items():
                print(f"  {collection}: {count} documents")
            return
        
        # Parse query if provided
        query = None
        if args.query:
            try:
                query = json.loads(args.query)
                print(f"🔍 Using query filter: {query}")
            except json.JSONDecodeError:
                print(f"❌ Invalid query JSON: {args.query}")
                sys.exit(1)
        
        # Export collections
        exported_files = []
        
        if args.all or not args.collection:
            # Export all collections
            exported_files = exporter.export_all_collections(args.format, query)
        else:
            # Export specific collection
            print(f"\n📦 Exporting collection: {args.collection}")
            
            if args.format == 'json':
                filepath = exporter.export_to_json(args.collection, query, args.output)
            elif args.format == 'csv':
                filepath = exporter.export_to_csv(args.collection, query, args.output)
            elif args.format == 'excel':
                filepath = exporter.export_to_excel(args.collection, query, args.output)
            
            exported_files.append(filepath)
        
        # Create backup manifest
        if exported_files:
            exporter.create_backup_manifest(exported_files)
        
        print(f"\n🎉 Export completed! Files saved to: {exporter.export_dir}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Export cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Export failed: {str(e)}")
        sys.exit(1)
    finally:
        exporter.disconnect()


if __name__ == '__main__':
    main()