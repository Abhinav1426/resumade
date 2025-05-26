import io
import json
from flask import Flask, request, Response

from jsonTopdf_tester.JsonToPDFBuilder import JsonToPDFBuilder


class ResumeServer:
    def __init__(self, host='0.0.0.0', port=5000, debug=True):
        self.app = Flask(__name__)
        self.builder = JsonToPDFBuilder()
        self.host = host
        self.port = port
        self.debug = debug
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/', methods=['GET'])
        def index():
            # Simple HTML form for JSON input or file upload
            return ("""
            <html>
              <head><title>Resume PDF Generator</title></head>
              <body style="font-family:sans-serif; margin:40px;">
                <h1>Resume PDF Generator</h1>
                <form action="/generate" method="post" enctype="multipart/form-data">
                  <p>Paste JSON below:</p>
                  <textarea name="json_data" rows="20" cols="80"></textarea><br/><br/>
                  <p>-- or upload a JSON file --</p>
                  <input type="file" name="json_file" accept="application/json"/><br/><br/>
                  <button type="submit">Generate PDF</button>
                </form>
              </body>
            </html>
            """)

        @self.app.route('/generate', methods=['POST'])
        def generate():
            # Load JSON from uploaded file or textarea
            if 'json_file' in request.files and request.files['json_file'].filename:
                data = json.load(request.files['json_file'])
            else:
                data = json.loads(request.form.get('json_data', '{}'))

            custom_order = [
                'personal_info',
                'summary',
                'education',
                'experiences',
                'skills',
                'projects',
                'languages',
                'extras',
                'awards',
                'certifications',
            ]
            # Build PDF bytes
            pdf_bytes = self.builder.build(data, order=custom_order)

            # Return PDF in browser
            return Response(
                pdf_bytes,
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': 'inline; filename=resume.pdf'
                }
            )

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug)


if __name__ == '__main__':
    server = ResumeServer()
    server.run()
