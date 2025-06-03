from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', static_url_path='')

UPLOAD_BUCKET = 'your-bucket-name'  # Replace with your AWS S3 bucket name
ALLOWED_EXTENSIONS = {'pdf', 'mp4', 'mov', 'avi'}  # Add more video formats as needed

s3 = boto3.client('s3', 
                  aws_access_key_id='YOUR_ACCESS_KEY',  # Replace with your AWS access key
                  aws_secret_access_key='YOUR_SECRET_KEY')  # Replace with your AWS secret key

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        if 'videoConfirmation' not in request.files or 'bankStatements' not in request.files:
            return jsonify({'error': 'Missing required files'}), 400

        video_file = request.files['videoConfirmation']
        bank_statements = request.files.getlist('bankStatements')

        # Validate and upload video file to S3
        if video_file and allowed_file(video_file.filename):
            video_filename = secure_filename(video_file.filename)
            video_key = f"videos/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video_filename}"
            s3.upload_fileobj(video_file, UPLOAD_BUCKET, video_key)
            video_path = f"https://{UPLOAD_BUCKET}.s3.amazonaws.com/{video_key}"
        else:
            return jsonify({'error': 'Invalid video file format or missing video'}), 400

        # Validate and upload bank statements (PDFs) to S3
        bank_statement_paths = []
        for file in bank_statements:
            if file and allowed_file(file.filename) and file.filename.lower().endsWith('.pdf'):
                filename = secure_filename(file.filename)
                file_key = f"statements/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                s3.upload_fileobj(file, UPLOAD_BUCKET, file_key)
                bank_statement_paths.append(f"https://{UPLOAD_BUCKET}.s3.amazonaws.com/{file_key}")
            else:
                return jsonify({'error': 'Invalid bank statement file format (must be PDF)'}), 400

        # Handle form data
        form_data = {
            'email': request.form.get('email'),
            'fullName': request.form.get('fullName'),
            'idPassport': request.form.get('idPassport'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'employer': request.form.get('employer'),
            'workAddress': request.form.get('workAddress'),
            'referral': request.form.get('referral'),
            'loanAmount': request.form.get('loanAmount'),
            'totalRepayment': request.form.get('totalRepayment'),
            'payment1Date': request.form.get('payment1Date'),
            'payment1Amount': request.form.get('payment1Amount'),
            'payment2Date': request.form.get('payment2Date'),
            'payment2Amount': request.form.get('payment2Amount'),
            'payment3Date': request.form.get('payment3Date'),
            'payment3Amount': request.form.get('payment3Amount'),
            'payment4Date': request.form.get('payment4Date'),
            'payment4Amount': request.form.get('payment4Amount'),
            'signature': request.form.get('signature'),
            'date': request.form.get('date'),
            'agreement': request.form.get('agreement') == 'on',
            'sendCopy': request.form.get('sendCopy') == 'on'
        }

        # Log form data (in production, save to a database or another storage)
        print("Form Data Received:", form_data)

        # Optionally, send a confirmation email if 'sendCopy' is checked
        if form_data['sendCopy']:
            # You would need an email service (e.g., SMTP, SendGrid) here
            print("Would send a copy to:", form_data['email'])

        return jsonify({
            'message': 'Form submitted successfully!',
            'data': form_data,
            'video_path': video_path,
            'bank_statements': bank_statement_paths
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)