import mimetypes
from app import create_app

# Windows'ta CSS ve JS dosyalarının doğru tanınmasını garantiye al
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)