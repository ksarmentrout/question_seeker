from backend.app import flask_app as api

if __name__ == '__main__':
    api.run(host='127.0.0.1', port=8000, threaded=True)
