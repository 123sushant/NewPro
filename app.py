from flask import Flask, request, jsonify, render_template
import numpy as np
import re
from urllib.parse import urlparse
from tld import get_tld
import pickle

# Load your trained model
with open('model.pkl', 'rb') as model_file:
    rf = pickle.load(model_file)

# Initialize the Flask app
app = Flask(__name__)

# Feature extraction functions
def having_ip_address(url):
    match = re.search(
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.' +
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|' +
        '((0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\/)|' +
        '(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}', url)
    return 1 if match else 0

def abnormal_url(url):
    hostname = urlparse(url).hostname
    hostname = str(hostname)
    match = re.search(hostname, url)
    return 1 if match else 0

def count_dot(url):
    return url.count('.')

def count_www(url):
    return url.count('www')

def count_atrate(url):
    return url.count('@')

def no_of_dir(url):
    urldir = urlparse(url).path
    return urldir.count('/')

def no_of_embed(url):
    urldir = urlparse(url).path
    return urldir.count('//')

def shortening_service(url):
    match = re.search(
        'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|yfrog\.com|' +
        'migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|short\.to|BudURL\.com|' +
        'ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|doiop\.com|short\.ie|kl\.am|' +
        'wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|' +
        'cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|' +
        'buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|' +
        'qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net',
        url)
    return 1 if match else 0

def count_https(url):
    return url.count('https')

def count_http(url):
    return url.count('http')

def count_per(url):
    return url.count('%')

def count_ques(url):
    return url.count('?')

def count_hyphen(url):
    return url.count('-')

def count_equal(url):
    return url.count('=')

def url_length(url):
    return len(str(url))

def hostname_length(url):
    return len(urlparse(url).netloc)

def suspicious_words(url):
    match = re.search(
        'PayPal|login|signin|bank|account|update|free|lucky|service|bonus|ebayisapi|webscr',
        url)
    return 1 if match else 0

def digit_count(url):
    return sum(1 for i in url if i.isdigit())

def letter_count(url):
    return sum(1 for i in url if i.isalpha())

def fd_length(url):
    urlpath = urlparse(url).path
    try:
        return len(urlpath.split('/')[1])
    except IndexError:
        return 0

def tld_length(url):
    try:
        tld = get_tld(url, fail_silently=True)
        return len(tld) if tld else -1
    except:
        return -1

def transform_url(url):
    """
    Transforms the input URL:
    - Removes 'http://', 'https://', and 'www.'
    - Adds a '.' before the domain.
    - Removes any trailing slash from the URL.
    """
    try:
        parsed_url = urlparse(url)
        # Remove trailing slash from the path if exists
        path = parsed_url.path.rstrip('/')
        domain_and_path = parsed_url.netloc.replace("www.", "") + path
        transformed_url = "." + domain_and_path
        return transformed_url
    except Exception as e:
        return f"Error: {str(e)}"

def get_prediction_from_url(test_url):
    """Get prediction based on URL features.""" 
    features = [
        having_ip_address(test_url),
        abnormal_url(test_url),
        count_dot(test_url),
        count_www(test_url),
        count_atrate(test_url),
        no_of_dir(test_url),
        no_of_embed(test_url),
        shortening_service(test_url),
        count_https(test_url),
        count_http(test_url),
        count_per(test_url),
        count_ques(test_url),
        count_hyphen(test_url),
        count_equal(test_url),
        url_length(test_url),
        hostname_length(test_url),
        suspicious_words(test_url),
        digit_count(test_url),
        letter_count(test_url),
        fd_length(test_url),
        tld_length(test_url)
    ]
    features = np.array(features).reshape(1, -1)
    pred = rf.predict(features)
    categories = ["SAFE", "DEFACEMENT", "PHISHING", "MALWARE"]
    return categories[int(pred[0])]

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for predicting the URL category."""
    data = request.json
    url = data.get('url', '')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # First, transform the URL
        transformed_url = transform_url(url)

        # Then, make the prediction based on transformed URL
        prediction = get_prediction_from_url(transformed_url)
        
        return jsonify({'url': url, 'transformed_url': transformed_url, 'prediction': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
