import cloudinary
import cloudinary.uploader
from flask import current_app
import logging
from datetime import datetime  # Add this import

class CloudinaryStorage:
    @staticmethod
    def upload_file(file, folder, public_id_prefix=None):
        """Upload a file to Cloudinary"""
        try:
            # Initialize Cloudinary with credentials
            cloudinary.config(
                cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
                api_key=current_app.config['CLOUDINARY_API_KEY'],
                api_secret=current_app.config['CLOUDINARY_API_SECRET']
            )
            
            # Create the public_id
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            public_id = f"{public_id_prefix}_{timestamp}" if public_id_prefix else timestamp
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                public_id=public_id,
                resource_type="auto",
                overwrite=True
            )
            
            return {
                'success': True,
                'public_id': result['public_id'],
                'secure_url': result['secure_url']
            }
            
        except Exception as e:
            current_app.logger.error(f"Cloudinary upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def delete_file(public_id):
        """Delete a file from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result['result'] == 'ok'
        except Exception as e:
            current_app.logger.error(f"Cloudinary delete error: {str(e)}")
            return False