from flask import Flask, Response, request
from flask_cors import CORS
from flask_cors import cross_origin
import subprocess

app = Flask(__name__)
# Configure CORS more specifically


@app.route('/run', methods=['POST', 'OPTIONS'])
@cross_origin(origin="http://localhost:3000", headers=["Content-Type"])
def stream_output():
    print("Received request to run main.py")
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    def generate():
        process = subprocess.Popen(
            ["python", "main.py", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        for raw_line in iter(process.stdout.readline, b''):  # read as bytes
            try:
                decoded_line = raw_line.decode("utf-8", errors="replace")  # decode safely
            except Exception as e:
                decoded_line = f"[Decode error]: {e}\n"

            yield decoded_line

        process.stdout.close()
        process.wait()

    response = Response(generate(), mimetype='text/plain')
    return response

if __name__ == "__main__":
    app.run(port=5000, debug=True)