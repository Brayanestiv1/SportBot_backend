import pymysql
import aiomysql
from app.config import settings

def get_sync_connection():
    """Get synchronous database connection"""
    connection_params = {
        'host': settings.DB_HOST,
        'port': settings.DB_PORT,
        'user': settings.DB_USER,
        'password': settings.DB_PASSWORD,
        'database': settings.DB_NAME,
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    # Only add SSL parameters if SSL CA is provided
    if settings.DB_SSL_CA:
        connection_params.update({
            'ssl_verify_cert': True,
            'ssl_verify_identity': True,
            'ssl_ca': settings.DB_SSL_CA
        })
    
    return pymysql.connect(**connection_params)

async def get_async_connection():
    """Get asynchronous database connection"""
    return await aiomysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        db=settings.DB_NAME,
        charset='utf8mb4',
        cursorclass=aiomysql.DictCursor
    )
